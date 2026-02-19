from datetime import date

from pydantic import BaseModel


class LFGStatus(BaseModel):
    user_id: int
    is_active: bool


class LFGStatusFromDB(LFGStatus):
    id: int

    class Config:
        from_attributes = True