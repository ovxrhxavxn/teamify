from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.setup import get_async_session
from .repositories import ProfileRepository
from .services import ProfileService


def get_profile_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> ProfileRepository:
    return ProfileRepository(session)


def get_profile_service(
    repo: Annotated[ProfileRepository, Depends(get_profile_repository)],
) -> ProfileService:
    return ProfileService(repo)