from pydantic import BaseModel


class GameRole(BaseModel):
    name: str


class GameRoleFromDB(GameRole):
    id: int

    class Config:
        from_attributes = True


class FaceitData(BaseModel):
    player_id: str
    user_id: int
    nickname: str
    elo: int
    lvl: int
    k_d_ratio: float
    avg_kills: float


class FaceitDataFromDB(FaceitData):
    id: int

    class Config:
        from_attributes = True


class FaceitAuthData(BaseModel):
    user_id: int
    refresh_token: str


class FaceitAuthDataFromDB(FaceitAuthData):
    id: int

    class Config:
        from_attributes = True