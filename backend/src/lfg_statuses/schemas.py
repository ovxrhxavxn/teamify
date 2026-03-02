from pydantic import BaseModel
from ..profiles.schemas import UserProfileResponse


class LFGStatusUpdate(BaseModel):
    is_active: bool

# Схема для ответа со списком активных игроков
class ActivePlayer(UserProfileResponse):
    pass
