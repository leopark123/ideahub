"""
消息相关 API
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.models.message import Message
from app.models.user import User
from app.repositories.message import MessageRepository
from app.schemas.message import (
    ConversationList,
    ConversationSummary,
    MessageCreate,
    MessageList,
    MessageResponse,
)

router = APIRouter()


@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "module": "messages"}


@router.get("/conversations", response_model=ConversationList)
async def get_conversations(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """获取所有会话列表"""
    repo = MessageRepository(db)
    conversations_data = await repo.get_conversations(current_user.id)

    conversations = []
    total_unread = 0

    for conv in conversations_data:
        user_data = None
        if conv["user"]:
            from app.schemas.user import UserBrief

            user_data = UserBrief(
                id=conv["user"].id,
                nickname=conv["user"].nickname,
                avatar=conv["user"].avatar,
                role=conv["user"].role,
            )

        last_msg = None
        if conv["last_message"]:
            last_msg = MessageResponse(
                id=conv["last_message"].id,
                sender_id=conv["last_message"].sender_id,
                receiver_id=conv["last_message"].receiver_id,
                content=conv["last_message"].content,
                message_type=conv["last_message"].message_type,
                attachment_url=conv["last_message"].attachment_url,
                attachment_name=conv["last_message"].attachment_name,
                is_read=conv["last_message"].is_read,
                read_at=conv["last_message"].read_at,
                project_id=conv["last_message"].project_id,
                created_at=conv["last_message"].created_at,
            )

        conversations.append(
            ConversationSummary(
                user_id=conv["user_id"],
                user=user_data,
                last_message=last_msg,
                unread_count=conv["unread_count"],
            )
        )
        total_unread += conv["unread_count"]

    return ConversationList(conversations=conversations, total_unread=total_unread)


@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """发送消息"""
    if data.receiver_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="不能给自己发送消息"
        )

    message = Message(
        sender_id=current_user.id,
        receiver_id=data.receiver_id,
        content=data.content,
        message_type=data.message_type,
        attachment_url=data.attachment_url,
        attachment_name=data.attachment_name,
        project_id=data.project_id,
    )

    repo = MessageRepository(db)
    return await repo.create(message)


@router.get("/conversation/{user_id}", response_model=MessageList)
async def get_conversation(
    user_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取与某用户的对话"""
    repo = MessageRepository(db)
    items, total = await repo.get_conversation(
        current_user.id, user_id, page, page_size
    )
    unread = await repo.get_unread_count(current_user.id)

    return MessageList(items=items, total=total, unread_count=unread)


@router.get("/unread/count")
async def get_unread_count(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """获取未读消息数量"""
    repo = MessageRepository(db)
    count = await repo.get_unread_count(current_user.id)
    return {"unread_count": count}


@router.post("/conversation/{user_id}/read")
async def mark_conversation_read(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """标记与某用户的对话为已读"""
    repo = MessageRepository(db)
    count = await repo.mark_conversation_as_read(current_user.id, user_id)
    return {"marked_count": count}


@router.post("/{message_id}/read", response_model=MessageResponse)
async def mark_message_read(
    message_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """标记消息为已读"""
    repo = MessageRepository(db)
    message = await repo.get_by_id(message_id)

    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="消息不存在")

    if message.receiver_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="没有权限操作此消息"
        )

    return await repo.mark_as_read(message)
