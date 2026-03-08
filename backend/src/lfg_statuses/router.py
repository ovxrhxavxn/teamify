import asyncio
import logging
from typing import Annotated, List, Optional

from fastapi import (
    APIRouter,
    Depends,
    WebSocket,
    WebSocketDisconnect,
    Query,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.setup import get_async_session
from ..auth.security import get_current_user
from ..auth.services import JWTService
from ..auth.dependencies import get_jwt_service
from ..users.schemas import UserFromDB
from ..users.services import UserService
from ..users.dependencies import get_user_service
from .schemas import LFGStatusUpdate, ActivePlayer
from .services import LFGStatusService
from .dependencies import get_lfg_status_service, get_lfg_status_repository
from .repositories import LFGStatusRepository
from ..websockets.dependencies import manager
from ..profiles.services import ProfileService
from ..profiles.dependencies import get_profile_service
from ..faceit.services import FaceitService
from ..faceit.dependencies import get_faceit_service


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/lfg", tags=["LFG"])


async def _build_player_broadcast_data(
    user_id: int,
    rating: float,
    profile_service: ProfileService,
    faceit_service: FaceitService,
) -> dict | None:
    """Собирает полные данные игрока для отправки через WS."""
    profile = await profile_service.get_by_user_id(user_id)
    faceit_data = await faceit_service.get_faceit_data_by_user_id(user_id)

    if not profile or not faceit_data:
        return None

    return {
        "profile": profile.model_dump(mode="json"),
        "faceit_data": faceit_data.model_dump(mode="json"),
        "rating": rating,
    }


async def get_current_user_from_token(
    token: str = Query(...),
    jwt_service: JWTService = Depends(get_jwt_service),
    user_service: UserService = Depends(get_user_service),
) -> UserFromDB:
    user_id = jwt_service.verify_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    user = await user_service.get(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


@router.get("/status", response_model=LFGStatusUpdate)
async def get_my_lfg_status(
    current_user: Annotated[UserFromDB, Depends(get_current_user)],
    lfg_repo: Annotated[LFGStatusRepository, Depends(get_lfg_status_repository)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    status_obj = await lfg_repo.get_or_create(current_user.id)
    await session.commit()
    return LFGStatusUpdate(is_active=status_obj.is_active)


@router.get("/active", response_model=List[ActivePlayer])
async def get_active_players(
    current_user: Annotated[UserFromDB, Depends(get_current_user)],
    lfg_service: Annotated[LFGStatusService, Depends(get_lfg_status_service)],
    offset: int = 0,
    limit: int = 3,
    min_elo: Optional[int] = Query(None),
    max_elo: Optional[int] = Query(None),
    min_rating: Optional[float] = Query(None),
    role_ids: Optional[List[int]] = Query(None),
):
    return await lfg_service.get_active_players(
        exclude_user_id=current_user.id,
        offset=offset,
        limit=limit,
        min_elo=min_elo,
        max_elo=max_elo,
        min_rating=min_rating,
        role_ids=role_ids,
    )


@router.post("/status")
async def set_lfg_status(
    status_update: LFGStatusUpdate,
    current_user: Annotated[UserFromDB, Depends(get_current_user)],
    lfg_service: Annotated[LFGStatusService, Depends(get_lfg_status_service)],
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
    faceit_service: Annotated[FaceitService, Depends(get_faceit_service)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    await lfg_service.set_status(current_user.id, status_update.is_active)
    await session.commit()

    if status_update.is_active:
        player_data = await _build_player_broadcast_data(
            user_id=current_user.id,
            rating=current_user.rating,
            profile_service=profile_service,
            faceit_service=faceit_service,
        )
        message = {
            "type": "player_joined",
            "player": player_data,
        }
    else:
        message = {
            "type": "player_left",
            "user_id": current_user.id,
        }

    await manager.broadcast(message, exclude_user_id=current_user.id)

    return {"status": "ok", "is_active": status_update.is_active}


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    current_user: Annotated[UserFromDB, Depends(get_current_user_from_token)],
    lfg_service: Annotated[LFGStatusService, Depends(get_lfg_status_service)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
    faceit_service: Annotated[FaceitService, Depends(get_faceit_service)],
):
    user_id = current_user.id
    conn = await manager.connect(websocket, user_id)

    try:
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=60.0,
                )
                if data == "ping":
                    await websocket.send_text("pong")
            except asyncio.TimeoutError:
                # Server-side keepalive
                try:
                    await websocket.send_text("ping")
                except Exception:
                    break

    except WebSocketDisconnect:
        logger.info("User %s WebSocket disconnected.", user_id)
    except Exception as e:
        logger.error("WebSocket error for user %s: %s", user_id, e)
    finally:
        manager.disconnect(user_id)

        try:
            lfg_status = await lfg_service._repo.get_or_create(user_id)
            if lfg_status.is_active:
                await lfg_service.set_status(user_id, False)
                await session.commit()

                leave_message = {
                    "type": "player_left",
                    "user_id": user_id,
                }
                await manager.broadcast(leave_message, exclude_user_id=user_id)
                logger.info("Auto-disabled LFG for disconnected user %s", user_id)
        except Exception as e:
            logger.error("Error auto-disabling LFG for user %s: %s", user_id, e)
