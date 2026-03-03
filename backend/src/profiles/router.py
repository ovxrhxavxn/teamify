import asyncio
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.setup import get_async_session
from ..auth.security import get_current_user
from ..users.schemas import UserFromDB
from ..users.services import UserService
from ..users.dependencies import get_user_service
from .services import ProfileService
from .dependencies import get_profile_service
from .schemas import UserProfileResponse, ProfileFromDB, ProfileUpdate, GameRoleSchema
from ..faceit.services import FaceitService
from ..faceit.dependencies import get_faceit_service
from ..reviews.services import ReviewsService
from ..reviews.dependencies import get_reviews_service

router = APIRouter(prefix="/profiles", tags=["Profiles"])


@router.get("/roles", response_model=List[GameRoleSchema])
async def get_all_game_roles(
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
):
    return await profile_service.get_all_roles()


@router.get("/me", response_model=UserProfileResponse)
async def get_my_profile(
    current_user: Annotated[UserFromDB, Depends(get_current_user)],
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
    faceit_service: Annotated[FaceitService, Depends(get_faceit_service)],
    reviews_service: Annotated[ReviewsService, Depends(get_reviews_service)],
):
    user_id = current_user.id

    profile = await profile_service.get_by_user_id(user_id)
    faceit_data = await faceit_service.get_faceit_data_by_user_id(user_id)

    if not profile or not faceit_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile or Faceit data not found.",
        )

    total_reviews = await reviews_service.get_total_reviews_for_profile(profile.id)

    return UserProfileResponse(
        profile=profile,
        faceit_data=faceit_data,
        rating=current_user.rating,
        total_reviews=total_reviews,
    )


@router.get("/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(
    user_id: int,
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
    faceit_service: Annotated[FaceitService, Depends(get_faceit_service)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    reviews_service: Annotated[ReviewsService, Depends(get_reviews_service)],
):
    profile = await profile_service.get_by_user_id(user_id)
    faceit_data = await faceit_service.get_faceit_data_by_user_id(user_id)
    user = await user_service.get(user_id)

    if not profile or not faceit_data or not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found.",
        )

    total_reviews = await reviews_service.get_total_reviews_for_profile(profile.id)

    return UserProfileResponse(
        profile=profile,
        faceit_data=faceit_data,
        rating=user.rating,
        total_reviews=total_reviews,
    )


@router.put("/me", response_model=ProfileFromDB)
async def update_my_profile(
    profile_data: ProfileUpdate,
    current_user: Annotated[UserFromDB, Depends(get_current_user)],
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    updated_profile = await profile_service.update_by_user_id(
        user_id=current_user.id,
        schema=profile_data,
    )
    if not updated_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found.",
        )
    await session.commit()
    return updated_profile