"""
请求日志中间件

功能:
- 记录所有 API 请求和响应
- 记录处理时间
- 敏感信息脱敏
- 支持结构化日志
"""

import time
import logging
import json
from typing import Callable, Set
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import Message

from app.core.config import settings


# 配置日志记录器
logger = logging.getLogger("api.access")

# 敏感字段列表 - 这些字段的值会被脱敏
SENSITIVE_FIELDS: Set[str] = {
    "password",
    "hashed_password",
    "secret_key",
    "access_token",
    "refresh_token",
    "authorization",
    "token",
    "api_key",
    "private_key",
}

# 不记录请求体的路径（二进制上传等）
SKIP_BODY_PATHS: Set[str] = {
    "/api/v1/uploads",
    "/api/v1/files",
}

# 健康检查等不记录的路径
SKIP_LOG_PATHS: Set[str] = {
    "/health",
    "/health/db",
    "/docs",
    "/redoc",
    "/openapi.json",
}


def mask_sensitive_data(data: dict) -> dict:
    """脱敏敏感字段"""
    if not isinstance(data, dict):
        return data

    masked = {}
    for key, value in data.items():
        lower_key = key.lower()
        if lower_key in SENSITIVE_FIELDS:
            masked[key] = "***MASKED***"
        elif isinstance(value, dict):
            masked[key] = mask_sensitive_data(value)
        elif isinstance(value, list):
            masked[key] = [
                mask_sensitive_data(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            masked[key] = value
    return masked


def get_client_ip(request: Request) -> str:
    """获取客户端真实 IP"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    return request.client.host if request.client else "unknown"


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    请求日志中间件

    记录格式:
    {
        "method": "POST",
        "path": "/api/v1/auth/login",
        "client_ip": "192.168.1.1",
        "status_code": 200,
        "duration_ms": 45.2,
        "user_agent": "Mozilla/5.0...",
        "request_id": "abc123"
    }
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 跳过不需要记录的路径
        path = request.url.path
        if any(path.startswith(skip) for skip in SKIP_LOG_PATHS):
            return await call_next(request)

        # 请求开始时间
        start_time = time.time()

        # 获取请求信息
        request_info = {
            "method": request.method,
            "path": path,
            "query_params": dict(request.query_params),
            "client_ip": get_client_ip(request),
            "user_agent": request.headers.get("User-Agent", ""),
        }

        # 开发环境记录请求体（脱敏后）
        if settings.ENVIRONMENT == "development":
            if not any(path.startswith(skip) for skip in SKIP_BODY_PATHS):
                try:
                    body = await request.body()
                    if body:
                        body_json = json.loads(body)
                        request_info["body"] = mask_sensitive_data(body_json)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    request_info["body"] = "<binary or invalid JSON>"

        # 处理请求
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            status_code = 500
            # 记录异常
            logger.exception(
                f"Request failed: {request.method} {path}",
                extra={"request_info": request_info, "error": str(e)},
            )
            raise

        # 计算处理时间
        duration_ms = (time.time() - start_time) * 1000

        # 构建日志记录
        log_data = {
            **request_info,
            "status_code": status_code,
            "duration_ms": round(duration_ms, 2),
        }

        # 根据状态码选择日志级别
        if status_code >= 500:
            logger.error(
                f"{request.method} {path} {status_code} ({duration_ms:.1f}ms)",
                extra=log_data,
            )
        elif status_code >= 400:
            logger.warning(
                f"{request.method} {path} {status_code} ({duration_ms:.1f}ms)",
                extra=log_data,
            )
        else:
            logger.info(
                f"{request.method} {path} {status_code} ({duration_ms:.1f}ms)",
                extra=log_data,
            )

        # 添加处理时间到响应头
        response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"

        return response


def setup_logging():
    """配置日志系统"""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # 根据环境选择日志格式
    if settings.ENVIRONMENT == "development":
        # 开发环境：简单格式，便于阅读
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s", datefmt="%H:%M:%S"
        )
    else:
        # 生产环境：JSON 格式，便于日志收集
        formatter = logging.Formatter(
            '{"time": "%(asctime)s", "level": "%(levelname)s", '
            '"logger": "%(name)s", "message": "%(message)s"}'
        )

    # 配置 API 访问日志
    api_handler = logging.StreamHandler()
    api_handler.setFormatter(formatter)
    api_handler.setLevel(log_level)

    api_logger = logging.getLogger("api.access")
    api_logger.addHandler(api_handler)
    api_logger.setLevel(log_level)
    api_logger.propagate = False

    # 配置应用日志
    app_handler = logging.StreamHandler()
    app_handler.setFormatter(formatter)
    app_handler.setLevel(log_level)

    app_logger = logging.getLogger("app")
    app_logger.addHandler(app_handler)
    app_logger.setLevel(log_level)
    app_logger.propagate = False

    return api_logger, app_logger
