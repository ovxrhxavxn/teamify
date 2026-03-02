from .repositories import AbstractReviewsRepository
from .schemas import (
    ReviewFromDB, 
    Review, 
    ReviewCreate, 
    ReviewWithAuthor, 
    ReviewAuthor
)
from ..users.repositories import AbstractUserRepository
from ..users.schemas import UserFromDB
from ..profiles.repositories import AbstractProfileRepository
from ..profiles.schemas import ProfileFromDB


class ReviewsService:
    def __init__(
            self, 
            repo: type[AbstractReviewsRepository[ReviewFromDB]], 
            user_repo: type[AbstractUserRepository[UserFromDB]],
            profle_repo: type[AbstractProfileRepository[ProfileFromDB]]
    ):

        self._repo = repo()
        self._user_repo = user_repo()
        self._profile_repo = profle_repo()


    async def add_review(self, schema: ReviewCreate, profile_id: int, author_id: int):
        review_data = schema.model_dump()
        review_data['profile_id'] = profile_id
        review_data['author_id'] = author_id
        
        # ПРАВИЛЬНЫЙ КОД: передаем словарь напрямую
        review_id = await self._repo.add(review_data)

        # --- НАЧАЛО НОВОЙ ЛОГИКИ ОБНОВЛЕНИЯ РЕЙТИНГА ---

        # 1. Пересчитываем средний рейтинг для профиля, на который оставили отзыв
        new_average_rating = await self._repo.get_average_rating_by_profile_id(profile_id)

        # 2. Находим, какому пользователю принадлежит этот профиль
        profile = await self._profile_repo.get(profile_id)
        if profile:
            # 3. Обновляем рейтинг этого пользователя в его таблице
            await self._user_repo.update_rating(profile.user_id, new_average_rating)

        # --- КОНЕЦ НОВОЙ ЛОГИКИ ---

        return review_id


    async def get_by_profile_id(self, profile_id: int, offset: int, limit: int):
        results = await self._repo.get_by_profile_id_with_author(profile_id, offset, limit)
        reviews_with_author = []
        for review, nickname, avatar in results:
            reviews_with_author.append(
                ReviewWithAuthor(
                    id=review.id,
                    content=review.content,
                    rating=review.rating,
                    created_at=review.created_at,
                    author=ReviewAuthor(nickname=nickname, avatar=avatar)
                )
            )
        return reviews_with_author