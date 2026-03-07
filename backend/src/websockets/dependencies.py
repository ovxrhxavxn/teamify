from typing import Dict
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        self.active_connections.pop(user_id, None)

    async def broadcast(self, message: dict, sender_id: int):
        disconnected = []
        for user_id, connection in self.active_connections.items():
            if user_id != sender_id:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.append(user_id)
        # Чистим мёртвые соединения
        for uid in disconnected:
            self.active_connections.pop(uid, None)



manager = ConnectionManager()