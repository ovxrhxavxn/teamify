from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse

from .services import JWTService
from .dependencies import get_jwt_service
from ..users.services import UserService
from ..users.dependencies import get_user_service
from .config import jwt_config

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/refresh")
async def refresh_access_token(
    request: Request,
    jwt_service: Annotated[JWTService, Depends(get_jwt_service)],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found",
        )

    user_id = jwt_service.verify_refresh_token(refresh_token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    user = await user_service.get(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    new_access_token = jwt_service.create_access_token(user_id)
    new_refresh_token = jwt_service.create_refresh_token(user_id)

    response = JSONResponse(
        content={"access_token": new_access_token, "token_type": "bearer"}
    )
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=jwt_config.REFRESH_TOKEN_EXPIRES * 24 * 60 * 60,
        path="/",
    )
    return response


@router.post("/logout")
async def logout():
    response = JSONResponse(content={"status": "ok"})
    response.delete_cookie(key="refresh_token", path="/")
    return response