from datetime import date

from pydantic import BaseModel, Field


class User(BaseModel):
    registration_date: date
    rating: float = Field(ge=0, le=5)


class UserFromDB(User):
    id: int

    class Config:
        from_attributes = True