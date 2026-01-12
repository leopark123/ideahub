"""
合伙人相关 Schema
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from app.models.partnership import PartnershipStatus, PartnershipRole
from app.schemas.user import UserBrief


class PartnershipBase(BaseModel):
    role: PartnershipRole = PartnershipRole.MEMBER
    position: Optional[str] = Field(None, max_length=100)
    responsibilities: Optional[str] = None
    equity_share: Optional[str] = Field(None, max_length=10)


class PartnershipApply(BaseModel):
    project_id: UUID
    role: PartnershipRole = PartnershipRole.MEMBER
    position: Optional[str] = Field(None, max_length=100)
    application_message: Optional[str] = None


class PartnershipUpdate(BaseModel):
    role: Optional[PartnershipRole] = None
    position: Optional[str] = Field(None, max_length=100)
    responsibilities: Optional[str] = None
    equity_share: Optional[str] = Field(None, max_length=10)
    status: Optional[PartnershipStatus] = None


class PartnershipResponse(PartnershipBase):
    id: UUID
    project_id: UUID
    user_id: UUID
    application_message: Optional[str] = None
    status: PartnershipStatus
    created_at: datetime

    class Config:
        from_attributes = True


class PartnershipDetail(PartnershipResponse):
    user: UserBrief


class PartnershipList(BaseModel):
    items: List[PartnershipDetail]
    total: int
