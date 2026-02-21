from .services import ReviewsService
from .repositories import ReviewsRepository


def get_reviews_service() -> ReviewsService:
    return ReviewsService(ReviewsRepository)