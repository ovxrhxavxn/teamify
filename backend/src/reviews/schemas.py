from datetime import date

from pydantic import BaseModel


class Review(BaseModel):
    profile_id: int
    author_id: int
    content:str
    rating: int
    created_at: date


class ReviewFromDB(Review):
    id: int

    class Config:
        from_attributes = True