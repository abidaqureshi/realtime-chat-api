from typing import List, Optional

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import Message
from app.respositories.base import BaseRepository


class ChatRepository(BaseRepository[Message]):
    def __init__(self, db:AsyncSession):
        super().__init__(Message, db)

    async def get_conversations(self, user1_id: int, user2_id: int, skip: int = 0, limit:int = 100) -> List[Message]:
        result = await self.db.execute(
            select(Message).where(
                ((Message.sender_id == user1_id) & (Message.receiver_id == user2_id)) |
                ((Message.sender_id == user2_id) & (Message.receiver_id == user1_id))
            ).order_by(Message.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        return result.scalars().all()

    async def mark_as_read(self, message_uuid:str) -> Optional[Message]:

        message = await self.get_by_uuid(message_uuid)
        if message and not message.is_read:
            message.is_read = True
            from datetime import datetime
            message.read_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(message)

        return message

    async def get_unread_messages(self, user_id:int) -> List[Message]:
        result = self.db.execute(select(Message).where(
            (Message.receiver_id == user_id) &
            (Message.is_read == False)
        ))

        return result.scalars().all()
