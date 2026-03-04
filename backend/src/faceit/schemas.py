from pydantic import BaseModel, HttpUrl, Field, field_validator
from typing import Optional, Union


# --- Схемы для работы с БД ---

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
    k_r_ratio: float
    avg_damage_per_round: float
    matches: int
    win_rate_percentage: float
    average_headshots_percentage: int
    longest_win_streak: int
    avatar: Optional[str] = None


class FaceitDataFromDB(FaceitData):
    id: int

    class Config:
        from_attributes = True


class FaceitAuthData(BaseModel):
    user_id: int
    encrypted_refresh_token: str


class FaceitAuthDataFromDB(FaceitAuthData):
    id: int

    class Config:
        from_attributes = True


# --- Схемы для парсинга ответов от API Faceit ---

class FaceitTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    id_token: str
    token_type: str
    expires_in: int


class FaceitUserInfoResponse(BaseModel):
    guid: str
    nickname: str
    given_name: str
    family_name: str
    picture: Union[HttpUrl, str, None] = None
    locale: str

    @field_validator("picture", mode="before")
    @classmethod
    def validate_picture(cls, v):
        if v == "":
            return None
        return v


class FaceitCS2Details(BaseModel):
    skill_level: int
    faceit_elo: int


class FaceitGames(BaseModel):
    cs2: Optional[FaceitCS2Details] = None


class FaceitPlayerDetailsResponse(BaseModel):
    player_id: str
    nickname: str
    games: FaceitGames
    avatar: Union[HttpUrl, str, None] = None

    @field_validator("avatar", mode="before")
    @classmethod
    def validate_avatar(cls, v):
        if v == "":
            return None
        return v


class FaceitPlayerStatsResponse(BaseModel):
    k_d_ratio: Optional[str] = Field(None, alias="Average K/D Ratio")
    k_r_ratio: Optional[str] = Field(None, alias="K/R Ratio")
    avg_damage_per_round: Optional[str] = Field(None, alias="ADR")
    win_rate_percentage: Optional[str] = Field(None, alias="Win Rate %")
    matches: Optional[str] = Field(None, alias="Matches")
    average_headshots_percentage: Optional[str] = Field(None, alias="Average Headshots %")
    longest_win_streak: Optional[str] = Field(None, alias="Longest Win Streak")


# --- Схемы для нашего API ---

class AppTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class FaceitCallbackPayload(BaseModel):
    code: str
    code_verifier: str
