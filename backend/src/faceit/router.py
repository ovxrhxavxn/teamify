from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.setup import get_async_session
from .services import FaceitAuthService
from .dependencies import get_faceit_auth_service
from .schemas import AppTokenResponse, FaceitCallbackPayload

router = APIRouter(prefix="/faceit", tags=["Faceit"])


@router.post("/oauth2/callback", response_model=AppTokenResponse)
async def faceit_auth_callback(
    payload: FaceitCallbackPayload,
    auth_service: Annotated[FaceitAuthService, Depends(get_faceit_auth_service)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    access_token = await auth_service.handle_callback(payload)
    await session.commit()
    return AppTokenResponse(access_token=access_token)