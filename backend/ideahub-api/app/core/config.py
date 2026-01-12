"""
配置管理

安全配置说明:
- 生产环境必须设置 SECRET_KEY 环境变量
- CORS 根据环境自动配置
- 敏感配置从环境变量读取
"""

import secrets
import warnings
from typing import List, Literal

from pydantic import computed_field, field_validator
from pydantic_settings import BaseSettings

# 开发环境默认 CORS 源
DEV_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:3002",
    "http://127.0.0.1:5173",
]


class Settings(BaseSettings):
    # 环境标识
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"

    # 数据库
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/ideahub"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # JWT - 安全配置
    SECRET_KEY: str = ""  # 必须从环境变量设置
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS - 生产环境从环境变量读取
    CORS_ORIGINS_STR: str = ""  # 逗号分隔的域名列表
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
    CORS_ALLOW_HEADERS: List[str] = [
        "Authorization",
        "Content-Type",
        "X-Requested-With",
        "Accept",
        "Origin",
        "X-CSRF-Token",
    ]

    # 文件上传
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    # 支付
    ALIPAY_APP_ID: str = ""
    ALIPAY_PRIVATE_KEY: str = ""
    ALIPAY_PUBLIC_KEY: str = ""

    # 日志
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    @computed_field
    @property
    def CORS_ORIGINS(self) -> List[str]:
        """根据环境返回 CORS 源列表"""
        if self.ENVIRONMENT == "development":
            return DEV_CORS_ORIGINS
        elif self.CORS_ORIGINS_STR:
            # 从环境变量解析
            return [
                origin.strip()
                for origin in self.CORS_ORIGINS_STR.split(",")
                if origin.strip()
            ]
        else:
            # 生产环境必须配置
            if self.ENVIRONMENT == "production":
                warnings.warn(
                    "生产环境未配置 CORS_ORIGINS_STR，将拒绝跨域请求", UserWarning
                )
            return []

    @field_validator("SECRET_KEY", mode="before")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """验证 SECRET_KEY 安全性"""
        # 不安全的默认值列表
        insecure_defaults = [
            "",
            "your-secret-key",
            "your-secret-key-change-in-production",
            "secret",
            "changeme",
            "password",
        ]

        if v in insecure_defaults:
            # 开发环境：自动生成临时密钥并警告
            generated_key = secrets.token_urlsafe(32)
            warnings.warn(
                f"\n{'='*60}\n"
                f"⚠️  警告: SECRET_KEY 未设置或使用了不安全的默认值!\n"
                f"已自动生成临时密钥用于开发环境。\n"
                f"生产环境必须设置环境变量 SECRET_KEY!\n"
                f'建议使用: python -c "import secrets; print(secrets.token_urlsafe(32))"\n'
                f"{'='*60}\n",
                UserWarning,
                stacklevel=2,
            )
            return generated_key

        # 检查密钥长度
        if len(v) < 32:
            warnings.warn(
                f"SECRET_KEY 长度不足 (当前: {len(v)} 字符)，建议至少 32 字符",
                UserWarning,
                stacklevel=2,
            )

        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# 生产环境额外检查
if settings.ENVIRONMENT == "production":
    if len(settings.SECRET_KEY) < 32:
        raise ValueError(
            "生产环境 SECRET_KEY 必须至少 32 字符！" "请设置环境变量 SECRET_KEY"
        )
