import asyncio
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from ..auth.security import get_current_user
from ..users.schemas import UserFromDB
from ..users.services import UserService
from ..users.dependencies import get_user_service
from ..users.schemas import UserFromDB
from .services import ProfileService
from .dependencies import get_profile_service
from .schemas import UserProfileResponse, ProfileFromDB, ProfileUpdate
from ..faceit.services import FaceitService
from ..faceit.dependencies import get_faceit_service


router = APIRouter(prefix="/profiles", tags=["Profiles"])


@router.get("/me", response_model=UserProfileResponse)
async def get_my_profile(
    current_user: Annotated[UserFromDB, Depends(get_current_user)],
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
    faceit_service: Annotated[FaceitService, Depends(get_faceit_service)],
):
    """
    Возвращает полную информацию о профиле текущего пользователя.
    """
    user_id = current_user.id
    # Используем asyncio.gather для параллельного выполнения запросов к БД
    profile_task = profile_service.get_by_user_id(user_id)
    faceit_data_task = faceit_service.get_faceit_data_by_user_id(user_id)
    results = await asyncio.gather(profile_task, faceit_data_task, return_exceptions=True)
    profile, faceit_data = results
    for result in results:
        if isinstance(result, Exception):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not fetch profile data."
            )
    if not profile or not faceit_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile or Faceit data not found for the user."
        )
    return UserProfileResponse(
        profile=profile,
        faceit_data=faceit_data,
        rating=current_user.rating
    )


@router.get("/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(
    user_id: int,
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
    faceit_service: Annotated[FaceitService, Depends(get_faceit_service)],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    """
    Возвращает полную информацию о профиле по ID пользователя.
    """
    profile_task = profile_service.get_by_user_id(user_id)
    faceit_data_task = faceit_service.get_faceit_data_by_user_id(user_id)
    user_task = user_service.get(user_id)
    results = await asyncio.gather(profile_task, faceit_data_task, user_task, return_exceptions=True)
    profile, faceit_data, user = results
    # Проверяем, что оба запроса завершились успешно
    for result in results:
        if isinstance(result, Exception):
            # Если произошла внутренняя ошибка сервера
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not fetch profile data."
            )
    if not profile or not faceit_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found."
        )
    return UserProfileResponse(
        profile=profile,
        faceit_data=faceit_data,
        rating=user.rating
    )


@router.put("/me", response_model=ProfileFromDB)
async def update_my_profile(
    profile_data: ProfileUpdate, # Тело запроса с новым описанием
    current_user: Annotated[UserFromDB, Depends(get_current_user)],
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
):
    """
    Обновляет описание профиля текущего пользователя.
    """
    user_id = current_user.id
    updated_profile = await profile_service.update_by_user_id(
        user_id=user_id, 
        schema=profile_data
    )
    if not updated_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found for the user to update."
        )
    return updated_profile
