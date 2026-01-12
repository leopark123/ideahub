"""
项目服务

包含缓存支持:
- 单个项目查询缓存
- 项目列表缓存
- 自动缓存失效
"""

import json
from uuid import UUID
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project, ProjectStatus, ProjectCategory
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectList
from app.repositories.project import ProjectRepository
from app.core.cache import Cache, CacheKey, CacheTTL, invalidate_project_cache


class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ProjectRepository(db)

    async def create_project(self, data: ProjectCreate, owner: User) -> Project:
        project = Project(
            owner_id=owner.id,
            title=data.title,
            subtitle=data.subtitle,
            description=data.description,
            category=data.category,
            cover_image=data.cover_image,
            video_url=data.video_url,
            team_size=data.team_size,
            status=ProjectStatus.DRAFT,
        )

        # 处理列表字段转 JSON
        if data.images:
            project.images = json.dumps(data.images)
        if data.required_skills:
            project.required_skills = json.dumps(data.required_skills)

        result = await self.repo.create(project)

        # 清除项目列表缓存
        await invalidate_project_cache()

        return result

    async def get_project(self, project_id: UUID) -> Project:
        project = await self.repo.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在"
            )
        return project

    async def list_projects(
        self,
        page: int = 1,
        page_size: int = 10,
        category: Optional[ProjectCategory] = None,
        project_status: Optional[ProjectStatus] = None,
        keyword: Optional[str] = None,
        owner_id: Optional[UUID] = None,
    ) -> ProjectList:
        items, total = await self.repo.list_projects(
            page=page,
            page_size=page_size,
            category=category,
            status=project_status,
            keyword=keyword,
            owner_id=owner_id,
        )

        return ProjectList(items=items, total=total, page=page, page_size=page_size)

    async def update_project(
        self, project_id: UUID, data: ProjectUpdate, current_user: User
    ) -> Project:
        project = await self.get_project(project_id)

        # 检查权限
        if project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="没有权限修改此项目"
            )

        update_data = data.model_dump(exclude_unset=True)

        # 处理列表字段转 JSON
        if "images" in update_data and update_data["images"] is not None:
            update_data["images"] = json.dumps(update_data["images"])
        if (
            "required_skills" in update_data
            and update_data["required_skills"] is not None
        ):
            update_data["required_skills"] = json.dumps(update_data["required_skills"])

        for field, value in update_data.items():
            setattr(project, field, value)

        result = await self.repo.update(project)

        # 清除该项目及列表缓存
        await invalidate_project_cache(str(project_id))

        return result

    async def delete_project(self, project_id: UUID, current_user: User) -> None:
        project = await self.get_project(project_id)

        # 检查权限
        if project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="没有权限删除此项目"
            )

        await self.repo.delete(project)

        # 清除该项目及列表缓存
        await invalidate_project_cache(str(project_id))

    async def publish_project(self, project_id: UUID, current_user: User) -> Project:
        project = await self.get_project(project_id)

        # 检查权限
        if project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="没有权限发布此项目"
            )

        # 检查状态
        if project.status not in [ProjectStatus.DRAFT, ProjectStatus.PENDING]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只有草稿或待审核状态的项目可以发布",
            )

        project.status = ProjectStatus.ACTIVE
        result = await self.repo.update(project)

        # 发布后清除缓存
        await invalidate_project_cache(str(project_id))

        return result

    async def view_project(self, project_id: UUID) -> Project:
        project = await self.get_project(project_id)
        return await self.repo.increment_view_count(project)

    async def like_project(self, project_id: UUID) -> Project:
        project = await self.get_project(project_id)
        return await self.repo.increment_like_count(project)
