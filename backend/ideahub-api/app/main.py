"""
IdeaHub API 入口

包含:
- CORS 中间件
- 速率限制中间件
- 请求日志中间件
- 数据库连接池监控
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging_middleware import RequestLoggingMiddleware, setup_logging
from app.core.rate_limit import RateLimitMiddleware
from app.db.session import get_db_stats

# 初始化日志系统
setup_logging()

app = FastAPI(
    title="IdeaHub API",
    description="创意孵化平台 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 中间件 - 根据环境配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# 请求日志中间件
app.add_middleware(RequestLoggingMiddleware)

# 速率限制中间件（生产/预发布环境启用）
if settings.ENVIRONMENT in ("production", "staging"):
    app.add_middleware(RateLimitMiddleware)

# 路由
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "environment": settings.ENVIRONMENT}


@app.get("/health/db")
async def db_health():
    """数据库连接池状态（仅开发环境）"""
    if settings.ENVIRONMENT != "development":
        return {"detail": "仅开发环境可用"}
    return await get_db_stats()
