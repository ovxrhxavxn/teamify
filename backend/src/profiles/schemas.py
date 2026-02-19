from pydantic import BaseModel


class Profile(BaseModel):
    user_id: int
    description: str


class ProfileFromDB(Profile):
    id: int

    class Config:
        from_attributes = True