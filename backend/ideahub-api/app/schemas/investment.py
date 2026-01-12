"""
投资相关 Schema
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal

from app.models.investment import InvestmentStatus, PaymentMethod


class InvestmentBase(BaseModel):
    amount: Decimal = Field(..., gt=0)
    reward_tier_id: Optional[str] = None


class InvestmentCreate(InvestmentBase):
    crowdfunding_id: UUID
    payment_method: PaymentMethod


class InvestmentResponse(InvestmentBase):
    id: UUID
    investor_id: UUID
    crowdfunding_id: UUID
    payment_method: Optional[PaymentMethod] = None
    transaction_id: Optional[str] = None
    status: InvestmentStatus
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class InvestmentList(BaseModel):
    items: List[InvestmentResponse]
    total: int
    page: int
    page_size: int


class PaymentRequest(BaseModel):
    investment_id: UUID
    payment_method: PaymentMethod


class PaymentCallback(BaseModel):
    transaction_id: str
    status: str
    amount: Decimal
    timestamp: datetime
