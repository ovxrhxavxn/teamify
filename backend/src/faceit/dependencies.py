from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.setup import get_async_session
from .repositories import FaceitRepository, FaceitAPIClient
from .services import FaceitService, FaceitAuthService
from ..users.dependencies import get_user_repository
from ..users.repositories import UserRepository
from ..profiles.dependencies import get_profile_repository
from ..profiles.repositories import ProfileRepository
from ..encryption.dependencies import get_encryption_service
from ..encryption.services import EncryptionService
from ..auth.dependencies import get_jwt_service
from ..auth.services import JWTService


def get_faceit_api_client() -> FaceitAPIClient:
    return FaceitAPIClient()


def get_faceit_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> FaceitRepository:
    return FaceitRepository(session)


def get_faceit_service(
    repo: Annotated[FaceitRepository, Depends(get_faceit_repository)],
    api_client: Annotated[FaceitAPIClient, Depends(get_faceit_api_client)],
) -> FaceitService:
    return FaceitService(repo, api_client)


def get_faceit_auth_service(
    faceit_service: Annotated[FaceitService, Depends(get_faceit_service)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    profile_repo: Annotated[ProfileRepository, Depends(get_profile_repository)],
    encryption_service: Annotated[EncryptionService, Depends(get_encryption_service)],
    jwt_service: Annotated[JWTService, Depends(get_jwt_service)],
) -> FaceitAuthService:
    return FaceitAuthService(
        faceit_service=faceit_service,
        user_repo=user_repo,
        profile_repo=profile_repo,
        encryption_service=encryption_service,
        jwt_service=jwt_service,
    )