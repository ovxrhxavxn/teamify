from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.setup import get_async_session
from .repositories import LFGStatusRepository
from .services import LFGStatusService


def get_lfg_status_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> LFGStatusRepository:
    return LFGStatusRepository(session)


def get_lfg_status_service(
    repo: Annotated[LFGStatusRepository, Depends(get_lfg_status_repository)],
) -> LFGStatusService:
    return LFGStatusService(repo)
