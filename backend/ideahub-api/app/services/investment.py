"""
投资服务

包含事务管理，确保投资操作的原子性。
"""

from uuid import UUID
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.investment import Investment, InvestmentStatus, PaymentMethod
from app.models.crowdfunding import CrowdfundingStatus
from app.models.user import User
from app.schemas.investment import InvestmentCreate
from app.repositories.investment import InvestmentRepository
from app.repositories.crowdfunding import CrowdfundingRepository
from app.db.transaction import UnitOfWork


class InvestmentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = InvestmentRepository(db)
        self.crowdfunding_repo = CrowdfundingRepository(db)

    async def create_investment(
        self, data: InvestmentCreate, current_user: User
    ) -> Investment:
        # 获取众筹
        crowdfunding = await self.crowdfunding_repo.get_by_id(data.crowdfunding_id)
        if not crowdfunding:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="众筹活动不存在"
            )

        # 检查众筹状态
        if crowdfunding.status != CrowdfundingStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="该众筹活动未开放投资"
            )

        # 检查投资金额
        if data.amount < crowdfunding.min_investment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"最低投资金额为 {crowdfunding.min_investment} 元",
            )

        if crowdfunding.max_investment and data.amount > crowdfunding.max_investment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"最高投资金额为 {crowdfunding.max_investment} 元",
            )

        # 创建投资记录
        investment = Investment(
            investor_id=current_user.id,
            crowdfunding_id=data.crowdfunding_id,
            amount=data.amount,
            reward_tier_id=data.reward_tier_id,
            payment_method=data.payment_method,
            status=InvestmentStatus.PENDING,
        )

        return await self.repo.create(investment)

    async def confirm_investment(
        self, investment_id: UUID, transaction_id: str
    ) -> Investment:
        """
        确认投资支付 - 使用事务确保原子性

        操作包括:
        1. 更新投资状态为已支付
        2. 更新众筹已筹金额
        3. 更新众筹投资人数

        如果任一操作失败，所有更改将回滚。
        """
        investment = await self.repo.get_by_id(investment_id)
        if not investment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="投资记录不存在"
            )

        if investment.status != InvestmentStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="该投资已处理"
            )

        crowdfunding = await self.crowdfunding_repo.get_by_id(
            investment.crowdfunding_id
        )
        if not crowdfunding:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="众筹活动不存在"
            )

        # 使用工作单元确保事务原子性
        async with UnitOfWork(self.db) as uow:
            # 更新投资状态
            investment.status = InvestmentStatus.PAID
            investment.transaction_id = transaction_id
            uow.add(investment)

            # 更新众筹金额和投资人数
            crowdfunding.current_amount += investment.amount
            crowdfunding.investor_count += 1
            uow.add(crowdfunding)

            # 提交事务 - 原子操作
            await uow.commit()

        # 返回更新后的投资记录（重新加载以获取关联数据）
        return await self.repo.get_by_id(investment_id)

    async def get_user_investments(
        self, user_id: UUID, page: int = 1, page_size: int = 10
    ):
        return await self.repo.get_by_user(user_id, page, page_size)

    async def get_investment(self, investment_id: UUID) -> Investment:
        investment = await self.repo.get_by_id(investment_id)
        if not investment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="投资记录不存在"
            )
        return investment
