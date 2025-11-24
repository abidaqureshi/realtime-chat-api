import json
from typing import Dict, List
from fastapi import WebSocket
import redis.asyncio as redis
from app.core.config import settings


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.redis_client = redis.from_url(settings.REDIS_URL)

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket

        # Store user online status in Redis
        await self.redis_client.set(f"user:{user_id}:status", "online")
        await self.redis_client.publish("user_status", json.dumps({
            "user_id": user_id,
            "status": "online"
        }))

    async def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

        # Update user status in Redis
        await self.redis_client.set(f"user:{user_id}:status", "offline")
        await self.redis_client.publish("user_status", json.dumps({
            "user_id": user_id,
            "status": "offline"
        }))

    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)

    async def get_online_users(self) -> List[str]:
        return list(self.active_connections.keys())

    async def is_user_online(self, user_id: str) -> bool:
        status = await self.redis_client.get(f"user:{user_id}:status")
        return status == b"online"


connection_manager = ConnectionManager()
