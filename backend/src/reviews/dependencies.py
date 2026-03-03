from typing import Annotated

from fastapi import Depends

from .repositories import ReviewsRepository
from .services import ReviewsService
from ..users.dependencies import get_user_repository
from ..users.repositories import UserRepository
from ..profiles.dependencies import get_profile_repository
from ..profiles.repositories import ProfileRepository
from ..database.setup import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession


def get_reviews_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> ReviewsRepository:
    return ReviewsRepository(session)


def get_reviews_service(
    repo: Annotated[ReviewsRepository, Depends(get_reviews_repository)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    profile_repo: Annotated[ProfileRepository, Depends(get_profile_repository)],
) -> ReviewsService:
    return ReviewsService(repo, user_repo, profile_repo)
