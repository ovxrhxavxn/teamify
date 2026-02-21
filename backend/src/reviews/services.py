from .repositories import AbstractReviewsRepository
from .schemas import ReviewFromDB, Review


class ReviewsService:

    def __init__(self, repo: type[AbstractReviewsRepository[ReviewFromDB]]):
        self._repo = repo()


    async def add(self, schema: Review):
        review_id = await self._repo.add(schema.model_dump())

        return review_id
    

    async def get_by_profile_id(self, profile_id: int, offset: int, limit: int):
        reviews = await self._repo.get_by_profile_id(profile_id, offset, limit)

        return [ReviewFromDB.model_validate(review) for review in reviews]