from typing import Optional

from pydantic import BaseModel

from ..faceit.schemas import FaceitDataFromDB


class Profile(BaseModel):
    user_id: int
    description: str | None = None


class ProfileFromDB(Profile):
    id: int
    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    profile: ProfileFromDB
    faceit_data: FaceitDataFromDB
    rating: float
    total_reviews: Optional[int] = None

class ProfileUpdate(BaseModel):
    description: Optional[str] = None
