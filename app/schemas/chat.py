from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class MessageType(Enum):
    MESSAGE = 'message'
    READ_RECEIPT = 'read_receipt'
    USER_STATUS = 'user_status'
    NEW_MESSAGE = 'new_message'
    MESSAGE_READ = 'message_read'


class MessageBase(BaseModel):
    content: str
    receiver_username: str


class MessageCreate(MessageBase):
    pass


class MessageResponse(BaseModel):
    uuid: str
    content: str
    sender_username: str
    receiver_username: str
    is_read: bool
    read_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class WebSocketMessage(BaseModel):
    type: MessageType  # message, read_receipt, user_status
    data: dict
