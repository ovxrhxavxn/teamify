# backend/src/lfg_responses/router.py
from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.setup import get_async_session
from ..auth.security import get_current_user
from ..users.schemas import UserFromDB
from .schemas import LFGResponseCreate
from .services import LFGResponseService
from .dependencies import get_lfg_response_service

router = APIRouter(prefix="/lfg/responses", tags=["LFG Responses"])

@router.post("")
async def respond_to_player(
    payload: LFGResponseCreate,
    current_user: Annotated[UserFromDB, Depends(get_current_user)],
    response_service: Annotated[
        LFGResponseService, Depends(get_lfg_response_service)
    ],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    result = await response_service.respond_to_player(
        responder_id=current_user.id,
        target_user_id=payload.target_user_id,
    )
    await session.commit()
    return result
