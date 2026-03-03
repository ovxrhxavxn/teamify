from typing import Optional, List

from pydantic import BaseModel

from ..faceit.schemas import FaceitDataFromDB


class GameRoleSchema(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class Profile(BaseModel):
    user_id: int
    description: str | None = None


class ProfileFromDB(Profile):
    id: int

    roles: List[GameRoleSchema] = []
    
    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    profile: ProfileFromDB
    faceit_data: FaceitDataFromDB
    rating: float
    total_reviews: Optional[int] = None


class ProfileUpdate(BaseModel):
    description: Optional[str] = None
    role_ids: Optional[List[int]] = None