from .services import ReviewsService
from .repositories import ReviewsRepository
from ..users.repositories import UserRepository
from ..profiles.repositories import ProfileRepository



def get_reviews_service() -> ReviewsService:
    return ReviewsService(ReviewsRepository, UserRepository, ProfileRepository)