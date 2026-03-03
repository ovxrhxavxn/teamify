from .repositories import ReviewsRepository
from .schemas import (
    ReviewCreateResponse,
    ReviewCreate,
    ReviewWithAuthor,
    ReviewAuthor,
)
from ..users.repositories import UserRepository
from ..profiles.repositories import ProfileRepository


class ReviewsService:
    def __init__(
        self,
        repo: ReviewsRepository,
        user_repo: UserRepository,
        profile_repo: ProfileRepository,
    ):
        self._repo = repo
        self._user_repo = user_repo
        self._profile_repo = profile_repo

    async def add_review(
        self,
        schema: ReviewCreate,
        profile_id: int,
        author_id: int,
    ) -> ReviewCreateResponse:
        review_data = schema.model_dump()
        review_data["profile_id"] = profile_id
        review_data["author_id"] = author_id

        review_id = await self._repo.add(review_data)

        new_average_rating = await self._repo.get_average_rating_by_profile_id(profile_id)

        profile = await self._profile_repo.get(profile_id)
        if profile:
            await self._user_repo.update_rating(profile.user_id, new_average_rating)

        return ReviewCreateResponse(
            review_id=review_id,
            new_average_rating=new_average_rating,
        )

    async def get_by_profile_id(
        self,
        profile_id: int,
        offset: int,
        limit: int,
    ) -> list[ReviewWithAuthor]:
        results = await self._repo.get_by_profile_id_with_author(profile_id, offset, limit)

        return [
            ReviewWithAuthor(
                id=review.id,
                content=review.content,
                rating=review.rating,
                created_at=review.created_at,
                author=ReviewAuthor(nickname=nickname, avatar=avatar),
            )
            for review, nickname, avatar in results
        ]

    async def get_total_reviews_for_profile(self, profile_id: int) -> int:
        return await self._repo.count_by_profile_id(profile_id)