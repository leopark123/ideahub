#!/usr/bin/env python3
"""
IdeaHub 后端项目初始化脚本
用法: python init_backend.py [project_path]
"""

import os
import sys
from pathlib import Path

def create_directory(path: Path):
    path.mkdir(parents=True, exist_ok=True)
    print(f"  📁 {path}")

def create_file(path: Path, content: str = ""):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    print(f"  📄 {path}")

def init_backend(base_path: Path):
    print(f"\n🚀 初始化 IdeaHub 后端项目: {base_path}\n")
    
    # 目录结构
    dirs = [
        "app/api/v1/endpoints",
        "app/core",
        "app/db",
        "app/models",
        "app/schemas",
        "app/services",
        "app/repositories",
        "app/utils",
        "migrations/versions",
        "tests",
        "scripts",
    ]
    
    print("📂 创建目录结构:")
    for d in dirs:
        create_directory(base_path / d)
    
    # 创建 __init__.py
    print("\n📝 创建 __init__.py 文件:")
    for d in dirs:
        if d.startswith("app"):
            init_file = base_path / d / "__init__.py"
            create_file(init_file, "")
    
    # main.py
    main_py = '''"""
IdeaHub API 入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(
    title="IdeaHub API",
    description="创意孵化平台 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由
app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "ok"}
'''
    create_file(base_path / "app/main.py", main_py)
    
    # config.py
    config_py = '''"""
配置管理
"""
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # 数据库
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/ideahub"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # 文件上传
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # 支付
    ALIPAY_APP_ID: str = ""
    ALIPAY_PRIVATE_KEY: str = ""
    ALIPAY_PUBLIC_KEY: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()
'''
    create_file(base_path / "app/core/config.py", config_py)
    
    # security.py
    security_py = '''"""
安全相关: JWT, 密码加密
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(subject: str) -> str:
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
'''
    create_file(base_path / "app/core/security.py", security_py)
    
    # deps.py
    deps_py = '''"""
依赖注入
"""
from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import async_session
from app.core.security import decode_token
from app.models.user import User
from app.repositories.user import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="用户已被禁用")
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    return current_user
'''
    create_file(base_path / "app/core/deps.py", deps_py)
    
    # db/base.py
    base_py = '''"""
SQLAlchemy Base
"""
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, DateTime, func

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
'''
    create_file(base_path / "app/db/base.py", base_py)
    
    # db/session.py
    session_py = '''"""
数据库会话
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
'''
    create_file(base_path / "app/db/session.py", session_py)
    
    # api/v1/router.py
    router_py = '''"""
API 路由汇总
"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, projects, crowdfunding, messages

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户"])
api_router.include_router(projects.router, prefix="/projects", tags=["项目"])
api_router.include_router(crowdfunding.router, prefix="/crowdfunding", tags=["众筹"])
api_router.include_router(messages.router, prefix="/messages", tags=["消息"])
'''
    create_file(base_path / "app/api/v1/router.py", router_py)
    
    # requirements.txt
    requirements = '''fastapi>=0.109.0
uvicorn[standard]>=0.27.0
sqlalchemy>=2.0.0
asyncpg>=0.29.0
alembic>=1.13.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6
redis>=5.0.0
aiofiles>=23.2.0
httpx>=0.26.0
'''
    create_file(base_path / "requirements.txt", requirements)
    
    # requirements-dev.txt
    requirements_dev = '''pytest>=7.4.0
pytest-asyncio>=0.23.0
pytest-cov>=4.1.0
httpx>=0.26.0
black>=24.1.0
isort>=5.13.0
mypy>=1.8.0
ruff>=0.1.0
'''
    create_file(base_path / "requirements-dev.txt", requirements_dev)
    
    # .env.example
    env_example = '''DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/ideahub
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
'''
    create_file(base_path / ".env.example", env_example)
    
    # .gitignore
    gitignore = '''__pycache__/
*.py[cod]
*$py.class
.Python
.env
.venv/
venv/
*.egg-info/
.eggs/
dist/
build/
.mypy_cache/
.pytest_cache/
.coverage
htmlcov/
uploads/
'''
    create_file(base_path / ".gitignore", gitignore)
    
    # Dockerfile
    dockerfile = '''FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
    create_file(base_path / "Dockerfile", dockerfile)
    
    print("\n✅ 后端项目初始化完成!")
    print("\n📋 下一步:")
    print("   1. cd", base_path)
    print("   2. cp .env.example .env  # 配置环境变量")
    print("   3. pip install -r requirements.txt")
    print("   4. uvicorn app.main:app --reload")

if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("ideahub-api")
    init_backend(path)
