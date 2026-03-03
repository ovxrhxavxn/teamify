from typing import List, Annotated
from fastapi import APIRouter, Depends, status, HTTPException
from ..auth.security import get_current_user
from ..users.schemas import UserFromDB
from ..profiles.dependencies import get_profile_service
from ..profiles.services import ProfileService
from .schemas import ReviewWithAuthor, ReviewCreate, ReviewCreateResponse
from .services import ReviewsService
from .dependencies import  get_reviews_service
from ..dependencies import pagination


router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get("/{profile_id}", response_model=List[ReviewWithAuthor])
async def get_reviews_for_profile(
    profile_id: int,
    pagination_params: Annotated[dict, Depends(pagination)],
    reviews_service: Annotated[ReviewsService, Depends(get_reviews_service)]
):
    reviews = await reviews_service.get_by_profile_id(
        profile_id, **pagination_params
    )
    return reviews


@router.post("/{profile_id}", status_code=status.HTTP_201_CREATED, response_model=ReviewCreateResponse)
async def add_review_for_profile(
    profile_id: int,
    review_data: ReviewCreate,
    current_user: Annotated[UserFromDB, Depends(get_current_user)],
    reviews_service: Annotated[ReviewsService, Depends(get_reviews_service)],
    profile_service: Annotated[ProfileService, Depends(get_profile_service)] 
):
    # --- НАЧАЛО НОВОЙ ЛОГИКИ ПРОВЕРКИ ---
    # 1. Получаем профиль, на который пытаются оставить отзыв
    profile_to_review = await profile_service.get_by_id(profile_id)

    # 2. Проверяем, существует ли такой профиль вообще
    if not profile_to_review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found."
        )

    # 3. ГЛАВНАЯ ПРОВЕРКА: сравниваем ID владельца профиля с ID автора отзыва
    if profile_to_review.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot leave a review for your own profile."
        )
    # --- КОНЕЦ НОВОЙ ЛОГИКИ ПРОВЕРКИ ---

    response_data = await reviews_service.add_review(
        schema=review_data,
        profile_id=profile_id,
        author_id=current_user.id
    )
    return response_data