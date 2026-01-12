"""
投资仓储

优化说明:
- 使用 _load_relationships 统一加载关系
- 支持选择性加载关系，减少不必要的查询
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.investment import Investment, InvestmentStatus


class InvestmentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _load_relationships(self, investment: Investment) -> Investment:
        """按需加载投资关系（investor, crowdfunding）"""
        await self.db.refresh(investment, ["investor", "crowdfunding"])
        return investment

    async def get_by_id(self, investment_id: UUID) -> Optional[Investment]:
        result = await self.db.execute(
            select(Investment)
            .options(
                selectinload(Investment.investor), selectinload(Investment.crowdfunding)
            )
            .where(Investment.id == investment_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user(
        self, user_id: UUID, page: int = 1, page_size: int = 10
    ) -> tuple[List[Investment], int]:
        # Count
        count_result = await self.db.execute(
            select(func.count(Investment.id)).where(Investment.investor_id == user_id)
        )
        total = count_result.scalar() or 0

        # Items
        offset = (page - 1) * page_size
        result = await self.db.execute(
            select(Investment)
            .options(
                selectinload(Investment.investor), selectinload(Investment.crowdfunding)
            )
            .where(Investment.investor_id == user_id)
            .order_by(Investment.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        items = list(result.scalars().all())

        return items, total

    async def get_by_crowdfunding(self, crowdfunding_id: UUID) -> List[Investment]:
        result = await self.db.execute(
            select(Investment)
            .options(
                selectinload(Investment.investor), selectinload(Investment.crowdfunding)
            )
            .where(Investment.crowdfunding_id == crowdfunding_id)
            .where(
                Investment.status.in_(
                    [InvestmentStatus.PAID, InvestmentStatus.CONFIRMED]
                )
            )
            .order_by(Investment.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(
        self, investment: Investment, load_relations: bool = True
    ) -> Investment:
        """创建投资记录"""
        self.db.add(investment)
        await self.db.commit()
        await self.db.refresh(investment)
        if load_relations:
            return await self._load_relationships(investment)
        return investment

    async def update(
        self, investment: Investment, load_relations: bool = True
    ) -> Investment:
        """更新投资记录"""
        await self.db.commit()
        await self.db.refresh(investment)
        if load_relations:
            return await self._load_relationships(investment)
        return investment
