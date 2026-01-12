"""
合伙人仓储
"""

from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.partnership import Partnership, PartnershipStatus


class PartnershipRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, partnership_id: UUID) -> Optional[Partnership]:
        result = await self.db.execute(
            select(Partnership)
            .options(selectinload(Partnership.user), selectinload(Partnership.project))
            .where(Partnership.id == partnership_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_and_project(
        self, user_id: UUID, project_id: UUID
    ) -> Optional[Partnership]:
        result = await self.db.execute(
            select(Partnership)
            .options(selectinload(Partnership.user), selectinload(Partnership.project))
            .where(
                and_(
                    Partnership.user_id == user_id, Partnership.project_id == project_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_project(
        self,
        project_id: UUID,
        status: Optional[PartnershipStatus] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Partnership], int]:
        query = (
            select(Partnership)
            .options(selectinload(Partnership.user))
            .where(Partnership.project_id == project_id)
        )

        if status:
            query = query.where(Partnership.status == status)

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Paginate
        offset = (page - 1) * page_size
        query = query.order_by(Partnership.created_at.desc())
        query = query.offset(offset).limit(page_size)

        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def get_by_user(
        self,
        user_id: UUID,
        status: Optional[PartnershipStatus] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Partnership], int]:
        query = (
            select(Partnership)
            .options(selectinload(Partnership.user), selectinload(Partnership.project))
            .where(Partnership.user_id == user_id)
        )

        if status:
            query = query.where(Partnership.status == status)

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Paginate
        offset = (page - 1) * page_size
        query = query.order_by(Partnership.created_at.desc())
        query = query.offset(offset).limit(page_size)

        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def create(self, partnership: Partnership) -> Partnership:
        self.db.add(partnership)
        await self.db.commit()
        return await self.get_by_id(partnership.id)

    async def update(self, partnership: Partnership) -> Partnership:
        await self.db.commit()
        return await self.get_by_id(partnership.id)

    async def get_pending_count(self, project_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count()).where(
                and_(
                    Partnership.project_id == project_id,
                    Partnership.status == PartnershipStatus.PENDING,
                )
            )
        )
        return result.scalar() or 0
