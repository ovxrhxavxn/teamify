from typing import Optional, List

from sqlalchemy import select, update, insert
from sqlalchemy.orm import selectinload

from ..database.repositories import BaseRepository
from .models import LFGStatus
from ..users.models import User
from ..profiles.models import Profile, GameRole
from ..faceit.models import FaceitData


class LFGStatusRepository(BaseRepository):

    async def get_or_create(self, user_id: int) -> LFGStatus:
        query = select(LFGStatus).where(LFGStatus.user_id == user_id)
        result = await self._session.execute(query)
        lfg_status = result.scalar_one_or_none()

        if not lfg_status:
            stmt = (
                insert(LFGStatus)
                .values(user_id=user_id, is_active=False)
                .returning(LFGStatus)
            )
            result = await self._session.execute(stmt)
            lfg_status = result.scalar_one()
            await self._session.flush()

        return lfg_status

    async def update_status(self, user_id: int, is_active: bool) -> None:
        stmt = (
            update(LFGStatus)
            .where(LFGStatus.user_id == user_id)
            .values(is_active=is_active)
        )
        await self._session.execute(stmt)

    async def get_active_players_profiles(
        self,
        exclude_user_id: int,
        offset: int,
        limit: int,
        min_elo: Optional[int],
        max_elo: Optional[int],
        min_rating: Optional[float],
        role_ids: Optional[List[int]],
    ):
        query = (
            select(Profile, FaceitData, User)
            .join(User, Profile.user_id == User.id)
            .join(FaceitData, User.id == FaceitData.user_id)
            .join(LFGStatus, User.id == LFGStatus.user_id)
            .where(LFGStatus.is_active == True, User.id != exclude_user_id)
            .options(selectinload(Profile.roles))
        )

        if min_elo is not None:
            query = query.where(FaceitData.elo >= min_elo)
        if max_elo is not None:
            query = query.where(FaceitData.elo <= max_elo)
        if min_rating is not None:
            query = query.where(User.rating >= min_rating)
        if role_ids:
            query = query.where(Profile.roles.any(GameRole.id.in_(role_ids)))

        query = query.offset(offset).limit(limit)
        result = await self._session.execute(query)
        return result.all()