"""
消息仓储
"""

from typing import List, Tuple
from uuid import UUID
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.message import Message


class MessageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, message_id: UUID) -> Message:
        result = await self.db.execute(
            select(Message)
            .options(selectinload(Message.sender), selectinload(Message.receiver))
            .where(Message.id == message_id)
        )
        return result.scalar_one_or_none()

    async def get_conversation(
        self, user1_id: UUID, user2_id: UUID, page: int = 1, page_size: int = 50
    ) -> Tuple[List[Message], int]:
        query = (
            select(Message)
            .options(selectinload(Message.sender), selectinload(Message.receiver))
            .where(
                or_(
                    and_(
                        Message.sender_id == user1_id, Message.receiver_id == user2_id
                    ),
                    and_(
                        Message.sender_id == user2_id, Message.receiver_id == user1_id
                    ),
                )
            )
        )

        # 计算总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # 分页（按时间倒序）
        query = query.order_by(Message.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        items = result.scalars().all()

        return list(items), total

    async def get_unread_count(self, user_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count()).where(
                and_(Message.receiver_id == user_id, Message.is_read == False)
            )
        )
        return result.scalar()

    async def create(self, message: Message) -> Message:
        self.db.add(message)
        await self.db.commit()
        # 重新加载以获取完整的关系数据
        return await self.get_by_id(message.id)

    async def mark_as_read(self, message: Message) -> Message:
        from datetime import datetime

        message.is_read = True
        message.read_at = datetime.utcnow()
        await self.db.commit()
        # 重新加载以获取完整的关系数据
        return await self.get_by_id(message.id)

    async def mark_conversation_as_read(
        self, receiver_id: UUID, sender_id: UUID
    ) -> int:
        from datetime import datetime
        from sqlalchemy import update

        result = await self.db.execute(
            update(Message)
            .where(
                and_(
                    Message.receiver_id == receiver_id,
                    Message.sender_id == sender_id,
                    Message.is_read == False,
                )
            )
            .values(is_read=True, read_at=datetime.utcnow())
        )
        await self.db.commit()
        return result.rowcount

    async def get_conversations(self, user_id: UUID) -> List[dict]:
        """
        获取用户的所有会话列表 - 完全优化版本
        总共只需要 4 次数据库查询，无论会话数量多少

        性能对比:
        - 优化前: 3N+1 次查询 (100个会话 = 301次查询)
        - 优化后: 4 次查询 (100个会话 = 4次查询)
        """
        from sqlalchemy import case, desc, literal_column
        from sqlalchemy.dialects.postgresql import aggregate_order_by
        from app.models.user import User

        # Step 1: 获取所有会话的对方用户ID和最后消息时间 (1次查询)
        conv_subquery = (
            select(
                case(
                    (Message.sender_id == user_id, Message.receiver_id),
                    else_=Message.sender_id,
                ).label("other_user_id"),
                func.max(Message.created_at).label("last_message_time"),
            )
            .where(or_(Message.sender_id == user_id, Message.receiver_id == user_id))
            .group_by(literal_column("other_user_id"))
            .subquery()
        )

        conv_result = await self.db.execute(
            select(
                conv_subquery.c.other_user_id, conv_subquery.c.last_message_time
            ).order_by(desc(conv_subquery.c.last_message_time))
        )
        conv_data = conv_result.all()

        if not conv_data:
            return []

        # 提取所有对方用户ID，保持排序顺序
        other_user_ids = [row[0] for row in conv_data]
        last_times = {row[0]: row[1] for row in conv_data}

        # Step 2: 批量获取所有用户信息 (1次查询)
        users_result = await self.db.execute(
            select(User).where(User.id.in_(other_user_ids))
        )
        users_map = {user.id: user for user in users_result.scalars().all()}

        # Step 3: 批量获取每个会话的未读数 (1次查询)
        unread_query = (
            select(Message.sender_id, func.count().label("unread_count"))
            .where(
                and_(
                    Message.receiver_id == user_id,
                    Message.sender_id.in_(other_user_ids),
                    Message.is_read == False,
                )
            )
            .group_by(Message.sender_id)
        )

        unread_result = await self.db.execute(unread_query)
        unread_map = {row[0]: row[1] for row in unread_result.all()}

        # Step 4: 批量获取所有最后消息 (1次查询)
        # 获取所有可能的最后消息，使用时间戳精确匹配
        time_conditions = []
        for other_id, last_time in last_times.items():
            time_conditions.append(
                and_(
                    or_(
                        and_(
                            Message.sender_id == user_id,
                            Message.receiver_id == other_id,
                        ),
                        and_(
                            Message.sender_id == other_id,
                            Message.receiver_id == user_id,
                        ),
                    ),
                    Message.created_at == last_time,
                )
            )

        if time_conditions:
            last_msgs_result = await self.db.execute(
                select(Message).where(or_(*time_conditions))
            )
            last_messages = last_msgs_result.scalars().all()

            # 构建映射: other_user_id -> last_message
            last_messages_map = {}
            for msg in last_messages:
                other_id = (
                    msg.receiver_id if msg.sender_id == user_id else msg.sender_id
                )
                # 只保留每个会话的最新消息
                if (
                    other_id not in last_messages_map
                    or msg.created_at > last_messages_map[other_id].created_at
                ):
                    last_messages_map[other_id] = msg
        else:
            last_messages_map = {}

        # 组装结果，保持按最后消息时间排序
        conversations = []
        for other_user_id in other_user_ids:
            conversations.append(
                {
                    "user_id": str(other_user_id),
                    "user": users_map.get(other_user_id),
                    "last_message": last_messages_map.get(other_user_id),
                    "unread_count": unread_map.get(other_user_id, 0),
                }
            )

        return conversations
