from typing import Dict
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def broadcast(self, message: dict, sender_id: int):
        # Отправляем сообщение всем, кроме отправителя
        for user_id, connection in self.active_connections.items():
            if user_id != sender_id:
                await connection.send_json(message)


manager = ConnectionManager()