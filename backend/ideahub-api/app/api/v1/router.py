"""
API 路由汇总
"""

from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    users,
    projects,
    crowdfunding,
    messages,
    investments,
    partnerships,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户"])
api_router.include_router(projects.router, prefix="/projects", tags=["项目"])
api_router.include_router(crowdfunding.router, prefix="/crowdfunding", tags=["众筹"])
api_router.include_router(investments.router, prefix="/investments", tags=["投资"])
api_router.include_router(messages.router, prefix="/messages", tags=["消息"])
api_router.include_router(partnerships.router, prefix="/partnerships", tags=["合伙人"])
