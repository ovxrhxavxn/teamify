from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.setup import get_async_session
from ..auth.config import jwt_config
from .services import FaceitAuthService
from .dependencies import get_faceit_auth_service
from .schemas import FaceitCallbackPayload


router = APIRouter(prefix="/faceit", tags=["Faceit"])


@router.post("/oauth2/callback")
async def faceit_auth_callback(
    payload: FaceitCallbackPayload,
    auth_service: Annotated[FaceitAuthService, Depends(get_faceit_auth_service)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    access_token, refresh_token = await auth_service.handle_callback(payload)
    await session.commit()

    response = JSONResponse(
        content={"access_token": access_token, "token_type": "bearer"}
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=jwt_config.REFRESH_TOKEN_EXPIRES * 24 * 60 * 60,
        path="/",
    )
    return response
