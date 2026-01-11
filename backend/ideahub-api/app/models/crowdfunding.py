"""
众筹模型
"""
import uuid
from sqlalchemy import Column, String, Text, ForeignKey, Enum as SQLEnum, Numeric, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base, TimestampMixin


class CrowdfundingStatus(str, enum.Enum):
    PENDING = "pending"       # 待开始
    ACTIVE = "active"         # 进行中
    SUCCESS = "success"       # 成功
    FAILED = "failed"         # 失败
    CANCELLED = "cancelled"   # 已取消


class Crowdfunding(Base, TimestampMixin):
    __tablename__ = "crowdfundings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), unique=True, nullable=False)

    # 众筹目标
    target_amount = Column(Numeric(12, 2), nullable=False)  # 目标金额
    current_amount = Column(Numeric(12, 2), default=0)      # 当前金额
    min_investment = Column(Numeric(10, 2), default=100)    # 最低投资额
    max_investment = Column(Numeric(10, 2), nullable=True)  # 最高投资额

    # 时间
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)

    # 回报档位 (JSON 格式)
    reward_tiers = Column(Text, nullable=True)  # [{amount, title, description, limit, claimed}]

    # 状态
    status = Column(SQLEnum(CrowdfundingStatus), default=CrowdfundingStatus.PENDING)
    investor_count = Column(Numeric(10, 0), default=0)

    # 关系
    project = relationship("Project", back_populates="crowdfunding")
    investments = relationship("Investment", back_populates="crowdfunding", lazy="dynamic")
