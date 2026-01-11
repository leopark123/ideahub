"""
速率限制中间件

基于 Redis 的滑动窗口速率限制，防止 API 滥用。

使用示例:
    @router.post("/login")
    @rate_limit(max_requests=5, window_seconds=60)  # 每分钟最多5次
    async def login(...):
        ...
"""
import time
import hashlib
from functools import wraps
from typing import Optional, Callable
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

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
        except Exception:
            # Redis 不可用时，禁用速率限制
            return None
    return _redis_client


class RateLimitExceeded(HTTPException):
    """速率限制超出异常"""
    def __init__(self, retry_after: int = 60):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"请求过于频繁，请 {retry_after} 秒后重试",
            headers={"Retry-After": str(retry_after)}
        )


async def check_rate_limit(
    key: str,
    max_requests: int,
    window_seconds: int
) -> tuple[bool, int, int]:
    """
    检查速率限制（滑动窗口算法）

    Returns:
        (is_allowed, remaining, reset_time)
    """
    redis = get_redis()
    if redis is None:
        # Redis 不可用，放行
        return True, max_requests, 0

    now = time.time()
    window_start = now - window_seconds

    try:
        pipe = redis.pipeline()
        # 移除窗口外的请求
        pipe.zremrangebyscore(key, 0, window_start)
        # 统计窗口内的请求数
        pipe.zcard(key)
        # 添加当前请求
        pipe.zadd(key, {str(now): now})
        # 设置过期时间
        pipe.expire(key, window_seconds)
        results = await pipe.execute()

        current_requests = results[1]
        remaining = max(0, max_requests - current_requests - 1)
        reset_time = int(now + window_seconds)

        if current_requests >= max_requests:
            return False, 0, reset_time

        return True, remaining, reset_time
    except Exception:
        # Redis 错误时放行
        return True, max_requests, 0


def get_client_ip(request: Request) -> str:
    """获取客户端 IP"""
    # 支持反向代理
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def rate_limit(
    max_requests: int = 100,
    window_seconds: int = 60,
    key_func: Optional[Callable[[Request], str]] = None
):
    """
    速率限制装饰器

    Args:
        max_requests: 窗口内最大请求数
        window_seconds: 时间窗口（秒）
        key_func: 自定义 key 生成函数

    Example:
        @router.post("/login")
        @rate_limit(max_requests=5, window_seconds=60)
        async def login(request: Request, ...):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从 kwargs 中获取 request
            request = kwargs.get('request')
            if request is None:
                # 尝试从 args 中找 Request 对象
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break

            if request is None:
                # 无法获取 request，跳过限制
                return await func(*args, **kwargs)

            # 生成限制 key
            if key_func:
                limit_key = key_func(request)
            else:
                client_ip = get_client_ip(request)
                path = request.url.path
                limit_key = f"rate_limit:{path}:{client_ip}"

            # 检查限制
            allowed, remaining, reset_time = await check_rate_limit(
                limit_key, max_requests, window_seconds
            )

            if not allowed:
                raise RateLimitExceeded(retry_after=window_seconds)

            return await func(*args, **kwargs)
        return wrapper
    return decorator


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    全局速率限制中间件

    对所有 API 请求应用基础速率限制
    """

    # 不同路径的限制配置
    RATE_LIMITS = {
        # 认证相关 - 更严格
        "/api/v1/auth/login": (5, 60),      # 每分钟 5 次
        "/api/v1/auth/register": (3, 60),   # 每分钟 3 次
        "/api/v1/auth/refresh": (10, 60),   # 每分钟 10 次

        # 消息发送 - 防止刷屏
        "/api/v1/messages": (30, 60),       # 每分钟 30 条

        # 投资 - 防止重复提交
        "/api/v1/investments": (10, 60),    # 每分钟 10 次
    }

    # 默认限制: 每分钟 200 次
    DEFAULT_LIMIT = (200, 60)

    async def dispatch(self, request: Request, call_next):
        # 只对 POST/PUT/DELETE 方法限制
        if request.method not in ("POST", "PUT", "DELETE", "PATCH"):
            return await call_next(request)

        # 获取路径对应的限制
        path = request.url.path
        max_requests, window_seconds = self.DEFAULT_LIMIT

        for pattern, limit in self.RATE_LIMITS.items():
            if path.startswith(pattern):
                max_requests, window_seconds = limit
                break

        # 生成 key
        client_ip = get_client_ip(request)
        limit_key = f"rate_limit:{path}:{client_ip}"

        # 检查限制
        allowed, remaining, reset_time = await check_rate_limit(
            limit_key, max_requests, window_seconds
        )

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"detail": f"请求过于频繁，请 {window_seconds} 秒后重试"},
                headers={
                    "Retry-After": str(window_seconds),
                    "X-RateLimit-Limit": str(max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_time),
                }
            )

        # 继续处理请求
        response = await call_next(request)

        # 添加速率限制头
        response.headers["X-RateLimit-Limit"] = str(max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_time)

        return response
