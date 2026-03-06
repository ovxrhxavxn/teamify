from typing import Optional
from datetime import date

from pydantic import BaseModel


class LFGResponseCreate(BaseModel):
    target_user_id: int


class LFGResponseOut(BaseModel):
    id: int
    responder_id: int
    target_user_id: int
    status: str
    created_at: date

    class Config:
        from_attributes = True


class ResponseNotification(BaseModel):
    """То, что придёт по WebSocket"""
    type: str = "lfg_response"
    responder_nickname: str
    responder_avatar: Optional[str] = None
    responder_faceit_url: str
    responder_elo: int
    responder_lvl: int
    response_id: int
