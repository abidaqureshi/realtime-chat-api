from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, get_current_user
from app.respositories.chat_respositories import ChatRepository
from app.respositories.user_respositories import UserRepository
from app.services.chat_service import ChatService

from app.schemas.chat import MessageCreate, MessageResponse
from app.websockets.connection_manager import connection_manager
import json

router = APIRouter()


@router.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    auth_service = ChatService(user_repo, ChatRepository(db))

    # Verify token and get user
    from app.services.auth_service import AuthService
    auth_service_instance = AuthService(user_repo)
    token_data = await auth_service_instance.verify_token(token)

    if not token_data:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    user = await user_repo.get_by_username(token_data.username)
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await connection_manager.connect(websocket, user.username)

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            if message_data["type"] == "message":
                # Handle new message
                chat_service = ChatService(user_repo, ChatRepository(db))
                message_create = MessageCreate(
                    content=message_data["data"]["content"],
                    receiver_username=message_data["data"]["receiver"]
                )

                message = await chat_service.send_message(user.username, message_create)
                if message:
                    # Send to receiver if online
                    await connection_manager.send_personal_message(
                        json.dumps({
                            "type": "new_message",
                            "data": message.model_dump()
                        }),
                        message_data["data"]["receiver"]
                    )

            elif message_data["type"] == "read_receipt":
                # Handle read receipt
                chat_service = ChatService(user_repo, ChatRepository(db))
                message = await chat_service.mark_message_as_read(
                    message_data["data"]["message_uuid"],
                    user.username
                )

                if message:
                    # Notify sender that message was read
                    await connection_manager.send_personal_message(
                        json.dumps({
                            "type": "message_read",
                            "data": {
                                "message_uuid": message.uuid,
                                "read_at": message.read_at.isoformat()
                            }
                        }),
                        message.sender_username
                    )

    except WebSocketDisconnect:
        await connection_manager.disconnect(user.username)


@router.get("/conversation/{other_user}", response_model=list[MessageResponse])
async def get_conversation(
        other_user: str,
        skip: int = 0,
        limit: int = 100,
        current_user: str = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    user_repo = UserRepository(db)
    chat_repo = ChatRepository(db)
    chat_service = ChatService(user_repo, chat_repo)

    return await chat_service.get_conversation(current_user, other_user, skip, limit)


@router.post("/messages/read/{message_uuid}", response_model=MessageResponse)
async def mark_as_read(
        message_uuid: str,
        current_user: str = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    user_repo = UserRepository(db)
    chat_repo = ChatRepository(db)
    chat_service = ChatService(user_repo, chat_repo)

    message = await chat_service.mark_message_as_read(message_uuid, current_user)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )

    return message