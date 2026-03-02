# services.py
from .repositories import AbstractUserRepository
from ..profiles.schemas import UserProfileResponse, ProfileFromDB
from ..faceit.schemas import FaceitDataFromDB
from .models import LFGStatus


class LFGStatusService:

    def __init__(self, repo: type[AbstractUserRepository[LFGStatus]]):
        self._repo = repo()

    async def set_status(self, user_id: int, is_active: bool):
        await self._repo.get_or_create(user_id)
        await self._repo.update_status(user_id, is_active)

    async def get_active_players(self, exclude_user_id: int, offset: int, limit: int):
        profiles_data = await self._repo.get_active_players_profiles(
            exclude_user_id, offset=offset, limit=limit
        )
        active_players = []
        for profile, faceit_data, user in profiles_data:
            active_players.append(
                UserProfileResponse(
                    profile=ProfileFromDB.model_validate(profile),
                    faceit_data=FaceitDataFromDB.model_validate(faceit_data),
                    rating=user.rating
                )
            )
        return active_players