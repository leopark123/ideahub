"""
项目相关 API
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.models.project import ProjectCategory, ProjectStatus
from app.models.user import User
from app.schemas.project import (
    ProjectCreate,
    ProjectDetail,
    ProjectList,
    ProjectResponse,
    ProjectUpdate,
)
from app.services.project import ProjectService

router = APIRouter()


@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "module": "projects"}


@router.get("", response_model=ProjectList)
async def list_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    category: Optional[ProjectCategory] = None,
    status: Optional[ProjectStatus] = None,
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取项目列表"""
    service = ProjectService(db)
    return await service.list_projects(
        page=page,
        page_size=page_size,
        category=category,
        project_status=status,
        keyword=keyword,
    )


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建项目"""
    service = ProjectService(db)
    return await service.create_project(data, current_user)


@router.get("/{project_id}", response_model=ProjectDetail)
async def get_project(project_id: UUID, db: AsyncSession = Depends(get_db)):
    """获取项目详情"""
    service = ProjectService(db)
    project = await service.view_project(project_id)
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新项目"""
    service = ProjectService(db)
    return await service.update_project(project_id, data, current_user)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除项目"""
    service = ProjectService(db)
    await service.delete_project(project_id, current_user)


@router.post("/{project_id}/publish", response_model=ProjectResponse)
async def publish_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """发布项目"""
    service = ProjectService(db)
    return await service.publish_project(project_id, current_user)


@router.post("/{project_id}/like", response_model=ProjectResponse)
async def like_project(project_id: UUID, db: AsyncSession = Depends(get_db)):
    """点赞项目"""
    service = ProjectService(db)
    return await service.like_project(project_id)
