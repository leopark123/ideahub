"""
数据库会话配置

连接池参数说明:
- pool_size: 连接池保持的连接数 (默认 5)
- max_overflow: 超出 pool_size 后允许的临时连接数 (默认 10)
- pool_recycle: 连接回收时间(秒)，防止连接过期 (建议 1800=30分钟)
- pool_timeout: 获取连接的等待超时时间(秒)
- pool_pre_ping: 使用前检测连接是否有效
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings


def create_engine():
    """
    创建数据库引擎，根据环境配置不同的连接池策略
    """
    # 基础配置
    engine_kwargs = {
        "echo": settings.ENVIRONMENT == "development",  # 开发环境打印 SQL
        "pool_pre_ping": True,  # 使用前检测连接有效性
    }

    # 生产环境使用连接池
    if settings.ENVIRONMENT == "production":
        engine_kwargs.update(
            {
                "pool_size": 20,  # 保持 20 个连接
                "max_overflow": 30,  # 高峰时最多 50 个连接
                "pool_recycle": 1800,  # 30 分钟回收连接
                "pool_timeout": 30,  # 等待连接超时 30 秒
            }
        )
    elif settings.ENVIRONMENT == "staging":
        engine_kwargs.update(
            {
                "pool_size": 10,
                "max_overflow": 20,
                "pool_recycle": 1800,
                "pool_timeout": 30,
            }
        )
    else:
        # 开发环境使用较小的连接池
        engine_kwargs.update(
            {
                "pool_size": 5,
                "max_overflow": 10,
                "pool_recycle": 3600,  # 1 小时回收
                "pool_timeout": 30,
            }
        )

    return create_async_engine(settings.DATABASE_URL, **engine_kwargs)


# 创建引擎
engine = create_engine()

# 创建会话工厂
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db_stats() -> dict:
    """获取数据库连接池状态（用于监控）"""
    pool = engine.pool
    return {
        "pool_size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "invalid": pool.invalidatedcount() if hasattr(pool, "invalidatedcount") else 0,
    }
