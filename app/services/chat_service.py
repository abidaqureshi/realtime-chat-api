from typing import Optional, List

from app.respositories.chat_respositories import ChatRepository
from app.respositories.user_respositories import UserRepository
from app.schemas.chat import MessageCreate, MessageResponse
from app.tasks.notification_tasks import (
    send_push_notification,
    process_message_analytics,
    deliver_message_offline
)


class ChatService:
    def __init__(self, user_repository: UserRepository, chat_repository: ChatRepository):
        self.user_repository = user_repository
        self.chat_repository = chat_repository

    async def send_message(self, sender_username: str, message_data: MessageCreate) -> Optional[MessageResponse]:
        sender = await self.user_repository.get_by_username(sender_username)
        receiver = await self.user_repository.get_by_username(message_data.receiver_username)

        if not sender or not receiver:
            return None

        # Create message
        message_dict = {
            "content": message_data.content,
            "sender_id": sender.id,
            "receiver_id": receiver.id
        }

        message = await self.chat_repository.create(message_dict)
        if message:
            send_push_notification.delay(
                receiver.username,
                f"New message from {sender.username}",
                'new_message'
            )
            process_message_analytics.delay(message.uuid)
            from app.websockets.connection_manager import connection_manager
            if not await connection_manager.is_user_online(receiver.username):
                deliver_message_offline.delay(
                    receiver.username,
                    {
                        "message_uuid": message.uuid,
                        "content": message.content,
                        "sender": sender_username,
                        "timestamp": message.created_at.isoformat()

                    }
                )
        return message

    async def get_conversation(self, current_user: str, other_user: str, skip: int = 0, limit: int = 100) -> List[
        MessageResponse]:
        user1 = await self.user_repository.get_by_username(current_user)
        user2 = await self.user_repository.get_by_username(other_user)

        if not user1 or not user2:
            return []

        messages = await self.chat_repository.get_conversations(user1.id, user2.id, skip, limit)

        return [
            MessageResponse(
                uuid=msg.uuid,
                content=msg.content,
                sender_username=msg.sender.username,
                receiver_username=msg.receiver.username,
                is_read=msg.is_read,
                read_at=msg.read_at,
                created_at=msg.created_at
            )
            for msg in messages
        ]

    async def mark_message_as_read(self, message_uuid: str, current_user: str) -> Optional[MessageResponse]:
        message = await self.chat_repository.mark_as_read(message_uuid)

        if not message or message.receiver.username != current_user:
            return None

        return MessageResponse(
            uuid=message.uuid,
            content=message.content,
            sender_username=message.sender.username,
            receiver_username=message.receiver.username,
            is_read=message.is_read,
            read_at=message.read_at,
            created_at=message.created_at
        )
