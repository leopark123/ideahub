"""
投资模型
"""

import enum
import uuid

from sqlalchemy import Column, ForeignKey, Numeric, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin


class InvestmentStatus(str, enum.Enum):
    PENDING = "pending"  # 待支付
    PAID = "paid"  # 已支付
    CONFIRMED = "confirmed"  # 已确认
    REFUNDED = "refunded"  # 已退款
    CANCELLED = "cancelled"  # 已取消


class PaymentMethod(str, enum.Enum):
    ALIPAY = "alipay"
    WECHAT = "wechat"
    BANK = "bank"


class Investment(Base, TimestampMixin):
    __tablename__ = "investments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    investor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    crowdfunding_id = Column(
        UUID(as_uuid=True), ForeignKey("crowdfundings.id"), nullable=False
    )

    # 投资信息
    amount = Column(Numeric(10, 2), nullable=False)
    reward_tier_id = Column(String(50), nullable=True)  # 选择的回报档位

    # 支付信息
    payment_method = Column(SQLEnum(PaymentMethod), nullable=True)
    transaction_id = Column(String(100), nullable=True)  # 第三方支付交易号

    # 状态
    status = Column(SQLEnum(InvestmentStatus), default=InvestmentStatus.PENDING)
    notes = Column(Text, nullable=True)

    # 关系
    investor = relationship("User", back_populates="investments")
    crowdfunding = relationship("Crowdfunding", back_populates="investments")
