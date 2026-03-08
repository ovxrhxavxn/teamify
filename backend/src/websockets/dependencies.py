import logging
from typing import Dict, Optional
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class UserConnection:
    """Обёртка над WebSocket с метаданными пользователя."""

    def __init__(self, websocket: WebSocket, user_id: int):
        self.websocket = websocket
        self.user_id = user_id

    async def send_json(self, data: dict):
        try:
            await self.websocket.send_json(data)
        except Exception as e:
            logger.warning("Failed to send to user %s: %s", self.user_id, e)
            raise


class ConnectionManager:
    def __init__(self):
        # user_id -> UserConnection
        self.active_connections: Dict[int, UserConnection] = {}

    async def connect(self, websocket: WebSocket, user_id: int) -> UserConnection:
        """Принимает соединение. Если у пользователя уже есть — закрывает старое."""
        # Закрываем старое соединение, если есть
        if user_id in self.active_connections:
            old = self.active_connections[user_id]
            try:
                await old.websocket.close(code=4001, reason="New connection opened")
            except Exception:
                pass
            del self.active_connections[user_id]

        await websocket.accept()
        conn = UserConnection(websocket, user_id)
        self.active_connections[user_id] = conn
        logger.info("User %s connected. Total: %d", user_id, len(self.active_connections))
        return conn

    def disconnect(self, user_id: int):
        """Удаляет соединение из менеджера."""
        removed = self.active_connections.pop(user_id, None)
        if removed:
            logger.info(
                "User %s disconnected. Total: %d",
                user_id,
                len(self.active_connections),
            )

    def is_connected(self, user_id: int) -> bool:
        return user_id in self.active_connections

    def get_connection(self, user_id: int) -> Optional[UserConnection]:
        return self.active_connections.get(user_id)

    async def send_to_user(self, user_id: int, message: dict) -> bool:
        """Отправляет сообщение конкретному пользователю. Возвращает True если успешно."""
        conn = self.active_connections.get(user_id)
        if not conn:
            return False
        try:
            await conn.send_json(message)
            return True
        except Exception:
            self.disconnect(user_id)
            return False

    async def broadcast(self, message: dict, exclude_user_id: int | None = None):
        """
        Отправляет сообщение всем подключённым пользователям,
        кроме exclude_user_id.
        """
        disconnected = []
        for user_id, conn in self.active_connections.items():
            if user_id == exclude_user_id:
                continue
            try:
                await conn.send_json(message)
            except Exception:
                disconnected.append(user_id)

        for uid in disconnected:
            self.active_connections.pop(uid, None)
            logger.info("Cleaned dead connection for user %s", uid)

    @property
    def connected_count(self) -> int:
        return len(self.active_connections)


manager = ConnectionManager()
