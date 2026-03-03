from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query, HTTPException, status

from ..auth.security import get_current_user
from ..users.schemas import UserFromDB
from .schemas import LFGStatusUpdate, ActivePlayer
from .services import LFGStatusService
from .dependencies import get_lfg_status_service
from ..websockets.dependencies import manager
from ..profiles.services import ProfileService
from ..profiles.dependencies import get_profile_service
from ..faceit.services import FaceitService
from ..faceit.dependencies import get_faceit_service
from .repositories import LFGStatusRepository
from ..auth.services import JWTService
from ..users.services import UserService
from ..users.repositories import UserRepository


async def get_current_user_from_token(token: str = Query(...)) -> UserFromDB:
    jwt_service = JWTService()
    user_service = UserService(UserRepository) 
    user_id = jwt_service.verify_token(token)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = await user_service.get(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


router = APIRouter(prefix="/lfg", tags=["LFG"])


# Для HTTP-запросов используем стандартный get_current_user
@router.get("/status", response_model=LFGStatusUpdate)
async def get_my_lfg_status(current_user: Annotated[UserFromDB, Depends(get_current_user)]):
    repo = LFGStatusRepository()
    status_obj = await repo.get_or_create(current_user.id)
    return LFGStatusUpdate(is_active=status_obj.is_active)


@router.get("/active", response_model=List[ActivePlayer])
async def get_active_players(
    current_user: Annotated[UserFromDB, Depends(get_current_user)],
    lfg_service: Annotated[LFGStatusService, Depends(get_lfg_status_service)],
    offset: int = 0,
    limit: int = 3,
    min_elo: Optional[int] = Query(None, description="Минимальное значение ELO"),
    max_elo: Optional[int] = Query(None, description="Максимальное значение ELO"),
    min_rating: Optional[float] = Query(None, description="Минимальный рейтинг (1.0 - 5.0)"),
    role_ids: Optional[List[int]] = Query(None, description="Список ID требуемых ролей")

):
    return await lfg_service.get_active_players(
        exclude_user_id=current_user.id, 
        offset=offset, 
        limit=limit,
        min_elo=min_elo,
        max_elo=max_elo,
        min_rating=min_rating,
        role_ids=role_ids
    )


@router.post("/status")
async def set_lfg_status(
    status_update: LFGStatusUpdate,
    current_user: Annotated[UserFromDB, Depends(get_current_user)],
    lfg_service: Annotated[LFGStatusService, Depends(get_lfg_status_service)],
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
    faceit_service: Annotated[FaceitService, Depends(get_faceit_service)],
):
    await lfg_service.set_status(current_user.id, status_update.is_active)
    profile = await profile_service.get_by_user_id(current_user.id)
    faceit_data = await faceit_service.get_faceit_data_by_user_id(current_user.id)
    message = {
        "type": "status_update",
        "is_active": status_update.is_active,
        "user_profile": {
            "profile": profile.model_dump(mode='json'),
            "faceit_data": faceit_data.model_dump(mode='json'),
            "rating": current_user.rating
        }
    }
    await manager.broadcast(message, sender_id=current_user.id)
    return {"status": "ok", "is_active": status_update.is_active}


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    # Используем исправленную зависимость
    current_user: Annotated[UserFromDB, Depends(get_current_user_from_token)]
):
    user_id = current_user.id
    await manager.connect(websocket, user_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id)