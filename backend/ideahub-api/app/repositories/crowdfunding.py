"""
众筹仓储
"""

from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.crowdfunding import Crowdfunding, CrowdfundingStatus


class CrowdfundingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, crowdfunding_id: UUID) -> Optional[Crowdfunding]:
        result = await self.db.execute(
            select(Crowdfunding)
            .options(selectinload(Crowdfunding.project))
            .where(Crowdfunding.id == crowdfunding_id)
        )
        return result.scalar_one_or_none()

    async def get_by_project_id(self, project_id: UUID) -> Optional[Crowdfunding]:
        result = await self.db.execute(
            select(Crowdfunding)
            .options(selectinload(Crowdfunding.project))
            .where(Crowdfunding.project_id == project_id)
        )
        return result.scalar_one_or_none()

    async def list_active(self) -> List[Crowdfunding]:
        result = await self.db.execute(
            select(Crowdfunding)
            .options(selectinload(Crowdfunding.project))
            .where(Crowdfunding.status == CrowdfundingStatus.ACTIVE)
            .order_by(Crowdfunding.end_time)
        )
        return list(result.scalars().all())

    async def create(self, crowdfunding: Crowdfunding) -> Crowdfunding:
        self.db.add(crowdfunding)
        await self.db.commit()
        # 重新加载以获取完整的关系数据
        return await self.get_by_id(crowdfunding.id)

    async def update(self, crowdfunding: Crowdfunding) -> Crowdfunding:
        await self.db.commit()
        # 重新加载以获取完整的关系数据
        return await self.get_by_id(crowdfunding.id)

    async def list_crowdfundings(
        self,
        page: int = 1,
        page_size: int = 10,
        status: Optional[CrowdfundingStatus] = None,
    ) -> Tuple[List[Crowdfunding], int]:
        query = select(Crowdfunding).options(selectinload(Crowdfunding.project))

        if status:
            query = query.where(Crowdfunding.status == status)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Paginate
        query = query.order_by(Crowdfunding.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        items = result.scalars().all()

        return list(items), total
