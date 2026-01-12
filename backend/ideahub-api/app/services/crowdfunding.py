"""
众筹服务
"""

import json
from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.crowdfunding import Crowdfunding, CrowdfundingStatus
from app.models.project import ProjectStatus
from app.models.user import User
from app.repositories.crowdfunding import CrowdfundingRepository
from app.repositories.project import ProjectRepository
from app.schemas.crowdfunding import (
    CrowdfundingCreate,
    CrowdfundingStats,
    CrowdfundingUpdate,
)


class CrowdfundingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = CrowdfundingRepository(db)
        self.project_repo = ProjectRepository(db)

    def _to_naive_utc(self, dt: datetime) -> datetime:
        """将日期时间转换为不带时区的UTC日期时间

        如果输入带时区信息，先转换为UTC再移除时区
        如果输入不带时区信息，假定已经是UTC
        """
        if dt.tzinfo is not None:
            # 先转换为UTC，再移除时区信息
            from datetime import timezone

            utc_dt = dt.astimezone(timezone.utc)
            return utc_dt.replace(tzinfo=None)
        return dt

    async def create_crowdfunding(
        self, data: CrowdfundingCreate, current_user: User
    ) -> Crowdfunding:
        # 检查项目是否存在
        project = await self.project_repo.get_by_id(data.project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在"
            )

        # 检查权限
        if project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="没有权限为此项目创建众筹"
            )

        # 检查是否已有众筹
        existing = await self.repo.get_by_project_id(data.project_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="该项目已有众筹活动"
            )

        # 转换为不带时区的日期时间
        start_time = self._to_naive_utc(data.start_time)
        end_time = self._to_naive_utc(data.end_time)

        # 验证时间
        if end_time <= start_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="结束时间必须晚于开始时间",
            )

        crowdfunding = Crowdfunding(
            project_id=data.project_id,
            target_amount=data.target_amount,
            min_investment=data.min_investment,
            max_investment=data.max_investment,
            start_time=start_time,
            end_time=end_time,
            status=CrowdfundingStatus.PENDING,
        )

        if data.reward_tiers:
            crowdfunding.reward_tiers = json.dumps(
                [tier.model_dump() for tier in data.reward_tiers], default=str
            )

        # 更新项目状态
        project.status = ProjectStatus.FUNDING

        crowdfunding = await self.repo.create(crowdfunding)
        await self.project_repo.update(project)

        return crowdfunding

    async def get_crowdfunding(self, crowdfunding_id: UUID) -> Crowdfunding:
        crowdfunding = await self.repo.get_by_id(crowdfunding_id)
        if not crowdfunding:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="众筹活动不存在"
            )
        return crowdfunding

    async def get_by_project(self, project_id: UUID) -> Crowdfunding:
        crowdfunding = await self.repo.get_by_project_id(project_id)
        if not crowdfunding:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="该项目没有众筹活动"
            )
        return crowdfunding

    async def list_active(self):
        return await self.repo.list_active()

    async def update_crowdfunding(
        self, crowdfunding_id: UUID, data: CrowdfundingUpdate, current_user: User
    ) -> Crowdfunding:
        crowdfunding = await self.get_crowdfunding(crowdfunding_id)

        # 检查权限
        project = await self.project_repo.get_by_id(crowdfunding.project_id)
        if project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="没有权限修改此众筹"
            )

        # 只能修改未开始的众筹
        if crowdfunding.status == CrowdfundingStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="进行中的众筹不能修改"
            )

        update_data = data.model_dump(exclude_unset=True)

        if "reward_tiers" in update_data and update_data["reward_tiers"]:
            update_data["reward_tiers"] = json.dumps(
                [tier.model_dump() for tier in update_data["reward_tiers"]], default=str
            )

        for field, value in update_data.items():
            setattr(crowdfunding, field, value)

        return await self.repo.update(crowdfunding)

    async def start_crowdfunding(
        self, crowdfunding_id: UUID, current_user: User
    ) -> Crowdfunding:
        crowdfunding = await self.get_crowdfunding(crowdfunding_id)

        # 检查权限
        project = await self.project_repo.get_by_id(crowdfunding.project_id)
        if project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="没有权限操作此众筹"
            )

        if crowdfunding.status != CrowdfundingStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只有待开始的众筹可以启动",
            )

        crowdfunding.status = CrowdfundingStatus.ACTIVE
        crowdfunding.start_time = datetime.utcnow()

        return await self.repo.update(crowdfunding)

    def get_stats(self, crowdfunding: Crowdfunding) -> CrowdfundingStats:
        now = datetime.utcnow()
        days_remaining = max(0, (crowdfunding.end_time - now).days)
        progress = (
            float(crowdfunding.current_amount / crowdfunding.target_amount * 100)
            if crowdfunding.target_amount > 0
            else 0
        )

        return CrowdfundingStats(
            total_raised=crowdfunding.current_amount,
            investor_count=int(crowdfunding.investor_count),
            days_remaining=days_remaining,
            progress_percentage=round(progress, 2),
        )
