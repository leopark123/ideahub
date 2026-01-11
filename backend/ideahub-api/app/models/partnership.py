"""
合伙人模型
"""
import uuid
from sqlalchemy import Column, String, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base, TimestampMixin


class PartnershipStatus(str, enum.Enum):
    PENDING = "pending"       # 申请中
    APPROVED = "approved"     # 已批准
    REJECTED = "rejected"     # 已拒绝
    LEFT = "left"             # 已退出


class PartnershipRole(str, enum.Enum):
    FOUNDER = "founder"           # 创始人
    CO_FOUNDER = "co_founder"     # 联合创始人
    PARTNER = "partner"           # 合伙人
    ADVISOR = "advisor"           # 顾问
    MEMBER = "member"             # 团队成员


class Partnership(Base, TimestampMixin):
    __tablename__ = "partnerships"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # 角色与职责
    role = Column(SQLEnum(PartnershipRole), default=PartnershipRole.MEMBER)
    position = Column(String(100), nullable=True)  # 具体职位
    responsibilities = Column(Text, nullable=True)

    # 权益分配
    equity_share = Column(String(10), nullable=True)  # 股权比例，如 "10%"

    # 申请信息
    application_message = Column(Text, nullable=True)

    # 状态
    status = Column(SQLEnum(PartnershipStatus), default=PartnershipStatus.PENDING)

    # 关系
    project = relationship("Project", back_populates="partnerships")
    user = relationship("User", back_populates="partnerships")
