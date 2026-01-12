"""
消息相关 Schema
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from app.models.message import MessageType
from app.schemas.user import UserBrief


class MessageBase(BaseModel):
    content: str = Field(..., min_length=1)
    message_type: MessageType = MessageType.TEXT


class MessageCreate(MessageBase):
    receiver_id: UUID
    attachment_url: Optional[str] = None
    attachment_name: Optional[str] = None
    project_id: Optional[UUID] = None


class MessageResponse(MessageBase):
    id: UUID
    sender_id: UUID
    receiver_id: UUID
    attachment_url: Optional[str] = None
    attachment_name: Optional[str] = None
    is_read: bool
    read_at: Optional[datetime] = None
    project_id: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MessageDetail(MessageResponse):
    sender: UserBrief
    receiver: UserBrief


class MessageList(BaseModel):
    items: List[MessageResponse]
    total: int
    unread_count: int


class ConversationSummary(BaseModel):
    user_id: str
    user: Optional[UserBrief] = None
    last_message: Optional[MessageResponse] = None
    unread_count: int


class ConversationList(BaseModel):
    conversations: List[ConversationSummary]
    total_unread: int
