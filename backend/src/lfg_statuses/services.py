from typing import Optional, List

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


    async def get_active_players(
        self, 
        exclude_user_id: int, 
        offset: int, 
        limit: int,
        min_elo: Optional[int],
        max_elo: Optional[int],
        min_rating: Optional[float],
        role_ids: Optional[List[int]]
    ):
        profiles_data = await self._repo.get_active_players_profiles(
            exclude_user_id,
            offset=offset,
            limit=limit,
            min_elo=min_elo,
            max_elo=max_elo,
            min_rating=min_rating,
            role_ids=role_ids
        )
    # --- КОНЕЦ ИЗМЕНЕНИЙ ---
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