"""
消息模型
"""
import uuid
from sqlalchemy import Column, String, Text, Boolean, ForeignKey, Enum as SQLEnum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base, TimestampMixin


class MessageType(str, enum.Enum):
    TEXT = "text"             # 文本消息
    IMAGE = "image"           # 图片消息
    FILE = "file"             # 文件消息
    SYSTEM = "system"         # 系统消息
    NOTIFICATION = "notification"  # 通知消息


class Message(Base, TimestampMixin):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    receiver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # 消息内容
    content = Column(Text, nullable=False)
    message_type = Column(SQLEnum(MessageType), default=MessageType.TEXT)

    # 附件（用于图片和文件）
    attachment_url = Column(String(500), nullable=True)
    attachment_name = Column(String(200), nullable=True)

    # 状态
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)

    # 关联项目（可选，用于项目相关的消息）
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)

    # 关系
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_messages")
