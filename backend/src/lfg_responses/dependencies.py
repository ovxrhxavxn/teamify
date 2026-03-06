from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.setup import get_async_session
from .repositories import LFGResponseRepository
from .services import LFGResponseService
from ..faceit.services import FaceitService
from ..faceit.dependencies import get_faceit_service


def get_lfg_response_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> LFGResponseRepository:
    return LFGResponseRepository(session)


def get_lfg_response_service(
    repo: Annotated[LFGResponseRepository, Depends(get_lfg_response_repository)],
    faceit_service: Annotated[FaceitService, Depends(get_faceit_service)],
) -> LFGResponseService:
    return LFGResponseService(repo, faceit_service)
