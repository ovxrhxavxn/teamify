from .services import ProfileService
from .repositories import ProfileRepository


def get_profile_service() -> ProfileService:
    return ProfileService(ProfileRepository)