"""
用户模型
"""

import uuid
from sqlalchemy import Column, String, Boolean, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base, TimestampMixin


class UserRole(str, enum.Enum):
    USER = "user"
    CREATOR = "creator"
    INVESTOR = "investor"
    ADMIN = "admin"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)

    # 个人信息
    nickname = Column(String(50), nullable=True)
    avatar = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)

    # 专业信息
    skills = Column(Text, nullable=True)  # JSON 格式存储技能标签
    experience = Column(Text, nullable=True)

    # 状态
    role = Column(SQLEnum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # 关系
    projects = relationship("Project", back_populates="owner", lazy="dynamic")
    investments = relationship("Investment", back_populates="investor", lazy="dynamic")
    partnerships = relationship("Partnership", back_populates="user", lazy="dynamic")
    sent_messages = relationship(
        "Message",
        foreign_keys="Message.sender_id",
        back_populates="sender",
        lazy="dynamic",
    )
    received_messages = relationship(
        "Message",
        foreign_keys="Message.receiver_id",
        back_populates="receiver",
        lazy="dynamic",
    )
