"""
Redis 缓存层

功能:
- 通用缓存操作（get/set/delete）
- 缓存装饰器
- JSON 序列化支持
- 缓存失效策略
"""
import json
import hashlib
import functools
from typing import Optional, Any, Callable, TypeVar, Union
from datetime import timedelta
import logging

logger = logging.getLogger("app.cache")

# Redis 客户端（惰性初始化）
_redis_client = None


def get_redis():
    """获取 Redis 客户端"""
    global _redis_client
    if _redis_client is None:
        try:
            import redis.asyncio as redis
            from app.core.config import settings
            _redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
        except Exception as e:
            logger.warning(f"Redis 连接失败: {e}")
            return None
    return _redis_client


class CacheKey:
    """缓存键生成器"""

    # 缓存键前缀
    PREFIX = "ideahub"

    # 各模块缓存键
    PROJECT = f"{PREFIX}:project"
    PROJECT_LIST = f"{PREFIX}:projects"
    USER = f"{PREFIX}:user"
    CROWDFUNDING = f"{PREFIX}:crowdfunding"
    STATS = f"{PREFIX}:stats"

    @staticmethod
    def project(project_id: str) -> str:
        return f"{CacheKey.PROJECT}:{project_id}"

    @staticmethod
    def project_list(page: int = 1, category: str = None, **kwargs) -> str:
        """生成项目列表缓存键"""
        params = {"page": page, "category": category, **kwargs}
        # 过滤 None 值并排序
        filtered = {k: v for k, v in sorted(params.items()) if v is not None}
        params_hash = hashlib.md5(json.dumps(filtered).encode()).hexdigest()[:8]
        return f"{CacheKey.PROJECT_LIST}:{params_hash}"

    @staticmethod
    def user(user_id: str) -> str:
        return f"{CacheKey.USER}:{user_id}"

    @staticmethod
    def crowdfunding(crowdfunding_id: str) -> str:
        return f"{CacheKey.CROWDFUNDING}:{crowdfunding_id}"

    @staticmethod
    def stats(stat_type: str) -> str:
        return f"{CacheKey.STATS}:{stat_type}"


class CacheTTL:
    """缓存过期时间（秒）"""
    SHORT = 60          # 1 分钟
    MEDIUM = 300        # 5 分钟
    LONG = 3600         # 1 小时
    VERY_LONG = 86400   # 1 天


class Cache:
    """Redis 缓存操作类"""

    @staticmethod
    async def get(key: str) -> Optional[Any]:
        """获取缓存"""
        redis = get_redis()
        if redis is None:
            return None

        try:
            data = await redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.warning(f"缓存读取失败 [{key}]: {e}")
            return None

    @staticmethod
    async def set(
        key: str,
        value: Any,
        ttl: int = CacheTTL.MEDIUM
    ) -> bool:
        """设置缓存"""
        redis = get_redis()
        if redis is None:
            return False

        try:
            data = json.dumps(value, default=str, ensure_ascii=False)
            await redis.set(key, data, ex=ttl)
            return True
        except Exception as e:
            logger.warning(f"缓存写入失败 [{key}]: {e}")
            return False

    @staticmethod
    async def delete(key: str) -> bool:
        """删除缓存"""
        redis = get_redis()
        if redis is None:
            return False

        try:
            await redis.delete(key)
            return True
        except Exception as e:
            logger.warning(f"缓存删除失败 [{key}]: {e}")
            return False

    @staticmethod
    async def delete_pattern(pattern: str) -> int:
        """按模式删除缓存（慎用，生产环境避免使用 KEYS 命令）"""
        redis = get_redis()
        if redis is None:
            return 0

        try:
            # 使用 SCAN 替代 KEYS 以避免阻塞
            deleted = 0
            async for key in redis.scan_iter(pattern, count=100):
                await redis.delete(key)
                deleted += 1
            return deleted
        except Exception as e:
            logger.warning(f"缓存批量删除失败 [{pattern}]: {e}")
            return 0

    @staticmethod
    async def exists(key: str) -> bool:
        """检查缓存是否存在"""
        redis = get_redis()
        if redis is None:
            return False

        try:
            return await redis.exists(key) > 0
        except Exception as e:
            logger.warning(f"缓存检查失败 [{key}]: {e}")
            return False

    @staticmethod
    async def incr(key: str, amount: int = 1, ttl: int = None) -> Optional[int]:
        """原子递增"""
        redis = get_redis()
        if redis is None:
            return None

        try:
            value = await redis.incr(key, amount)
            if ttl:
                await redis.expire(key, ttl)
            return value
        except Exception as e:
            logger.warning(f"缓存递增失败 [{key}]: {e}")
            return None


T = TypeVar('T')


def cached(
    key_func: Callable[..., str],
    ttl: int = CacheTTL.MEDIUM,
    skip_if: Callable[..., bool] = None
):
    """
    缓存装饰器

    Args:
        key_func: 生成缓存键的函数，接收与被装饰函数相同的参数
        ttl: 缓存过期时间（秒）
        skip_if: 跳过缓存的条件函数

    Example:
        @cached(
            key_func=lambda project_id: CacheKey.project(str(project_id)),
            ttl=CacheTTL.MEDIUM
        )
        async def get_project(project_id: UUID) -> Project:
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            # 检查是否跳过缓存
            if skip_if and skip_if(*args, **kwargs):
                return await func(*args, **kwargs)

            # 生成缓存键
            cache_key = key_func(*args, **kwargs)

            # 尝试从缓存获取
            cached_data = await Cache.get(cache_key)
            if cached_data is not None:
                logger.debug(f"缓存命中: {cache_key}")
                return cached_data

            # 执行原函数
            result = await func(*args, **kwargs)

            # 缓存结果（如果不是 None）
            if result is not None:
                # 处理 Pydantic 模型
                if hasattr(result, 'model_dump'):
                    cache_value = result.model_dump()
                elif hasattr(result, '__dict__'):
                    cache_value = {k: v for k, v in result.__dict__.items()
                                   if not k.startswith('_')}
                else:
                    cache_value = result

                await Cache.set(cache_key, cache_value, ttl)
                logger.debug(f"缓存写入: {cache_key}")

            return result
        return wrapper
    return decorator


async def invalidate_project_cache(project_id: str = None):
    """
    使项目缓存失效

    Args:
        project_id: 具体项目 ID，如果为 None 则清除所有项目列表缓存
    """
    if project_id:
        await Cache.delete(CacheKey.project(project_id))

    # 清除项目列表缓存
    await Cache.delete_pattern(f"{CacheKey.PROJECT_LIST}:*")


async def invalidate_user_cache(user_id: str):
    """使用户缓存失效"""
    await Cache.delete(CacheKey.user(user_id))


async def invalidate_crowdfunding_cache(crowdfunding_id: str = None):
    """使众筹缓存失效"""
    if crowdfunding_id:
        await Cache.delete(CacheKey.crowdfunding(crowdfunding_id))
