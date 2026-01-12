"""
众筹相关 Schema
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.crowdfunding import CrowdfundingStatus


class RewardTier(BaseModel):
    id: str
    amount: Decimal
    title: str
    description: str
    limit: Optional[int] = None
    claimed: int = 0


class CrowdfundingBase(BaseModel):
    target_amount: Decimal = Field(..., gt=0)
    min_investment: Decimal = Field(default=100, ge=1)
    max_investment: Optional[Decimal] = None
    start_time: datetime
    end_time: datetime


class CrowdfundingCreate(CrowdfundingBase):
    project_id: UUID
    reward_tiers: Optional[List[RewardTier]] = None


class CrowdfundingUpdate(BaseModel):
    target_amount: Optional[Decimal] = Field(None, gt=0)
    min_investment: Optional[Decimal] = Field(None, ge=1)
    max_investment: Optional[Decimal] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    reward_tiers: Optional[List[RewardTier]] = None


class CrowdfundingResponse(CrowdfundingBase):
    id: UUID
    project_id: UUID
    current_amount: Decimal
    status: CrowdfundingStatus
    investor_count: int
    reward_tiers: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    # 从 project 关联获取
    title: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


class CrowdfundingDetail(CrowdfundingResponse):
    progress_percentage: float = 0.0


class CrowdfundingStats(BaseModel):
    total_raised: Decimal
    investor_count: int
    days_remaining: int
    progress_percentage: float


class CrowdfundingList(BaseModel):
    items: List[CrowdfundingResponse]
    total: int
    page: int
    page_size: int
