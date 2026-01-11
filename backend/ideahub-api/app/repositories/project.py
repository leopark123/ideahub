"""
项目仓储

优化说明:
- 使用 _load_relationships 统一加载关系
- refresh 后按需加载关系，避免多余查询
- 简单更新操作（如计数）不加载关系，提升性能
"""
from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.project import Project, ProjectStatus, ProjectCategory


class ProjectRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _load_relationships(self, project: Project) -> Project:
        """按需加载项目关系（owner）"""
        await self.db.refresh(project, ['owner'])
        return project

    async def get_by_id(self, project_id: UUID) -> Optional[Project]:
        result = await self.db.execute(
            select(Project)
            .options(selectinload(Project.owner))
            .where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    async def list_projects(
        self,
        page: int = 1,
        page_size: int = 10,
        category: Optional[ProjectCategory] = None,
        status: Optional[ProjectStatus] = None,
        keyword: Optional[str] = None,
        owner_id: Optional[UUID] = None
    ) -> Tuple[List[Project], int]:
        query = select(Project).options(selectinload(Project.owner))

        # 过滤条件
        if category:
            query = query.where(Project.category == category)
        if status:
            query = query.where(Project.status == status)
        if owner_id:
            query = query.where(Project.owner_id == owner_id)
        if keyword:
            query = query.where(
                or_(
                    Project.title.ilike(f"%{keyword}%"),
                    Project.description.ilike(f"%{keyword}%")
                )
            )

        # 计算总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # 分页
        query = query.order_by(Project.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        items = result.scalars().all()

        return list(items), total

    async def create(self, project: Project, load_relations: bool = True) -> Project:
        """创建项目"""
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        if load_relations:
            return await self._load_relationships(project)
        return project

    async def update(self, project: Project, load_relations: bool = True) -> Project:
        """更新项目"""
        await self.db.commit()
        await self.db.refresh(project)
        if load_relations:
            return await self._load_relationships(project)
        return project

    async def delete(self, project: Project) -> None:
        """删除项目"""
        await self.db.delete(project)
        await self.db.commit()

    async def increment_view_count(self, project: Project) -> Project:
        """增加浏览量 - 不加载关系，提升性能"""
        project.view_count = (project.view_count or 0) + 1
        await self.db.commit()
        await self.db.refresh(project)
        # 直接加载 owner 关系，比 get_by_id 更高效
        return await self._load_relationships(project)

    async def increment_like_count(self, project: Project) -> Project:
        """增加点赞数 - 不加载关系，提升性能"""
        project.like_count = (project.like_count or 0) + 1
        await self.db.commit()
        await self.db.refresh(project)
        # 直接加载 owner 关系，比 get_by_id 更高效
        return await self._load_relationships(project)
