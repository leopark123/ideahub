"""
用户相关 API
"""

import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter()


@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "module": "users"}


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    """获取用户信息"""
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    return user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新当前用户信息"""
    update_data = data.model_dump(exclude_unset=True)

    # 处理 skills 列表转 JSON
    if "skills" in update_data and update_data["skills"] is not None:
        update_data["skills"] = json.dumps(update_data["skills"])

    for field, value in update_data.items():
        setattr(current_user, field, value)

    repo = UserRepository(db)
    return await repo.update(current_user)


@router.get("/me/projects")
async def get_my_projects(current_user: User = Depends(get_current_user)):
    """获取我的项目列表"""
    projects = await current_user.projects.all()
    return {"items": projects, "total": len(projects)}


@router.get("/me/investments")
async def get_my_investments(current_user: User = Depends(get_current_user)):
    """获取我的投资记录"""
    investments = await current_user.investments.all()
    return {"items": investments, "total": len(investments)}
