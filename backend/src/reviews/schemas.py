from typing import Optional

from datetime import date

from pydantic import BaseModel, Field


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


class ReviewAuthor(BaseModel):
    nickname: str
    avatar: Optional[str] = None


class ReviewCreate(BaseModel):
    content: str
    rating: int = Field(ge=1, le=5) # Рейтинг от 1 до 5


class ReviewWithAuthor(BaseModel):
    id: int
    content: str
    rating: int
    created_at: date
    author: ReviewAuthor


class ReviewCreateResponse(BaseModel):
    review_id: int
    new_average_rating: float