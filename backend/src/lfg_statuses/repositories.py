from typing import Protocol, Optional, List

from sqlalchemy import select, update, insert
from sqlalchemy.orm import selectinload

from ..database.setup import async_session_maker
from .models import LFGStatus
from ..users.models import User
from ..profiles.models import Profile, GameRole
from ..faceit.models import FaceitData


class AbstractUserRepository[Entity](Protocol):

    async def get_or_create(self, user_id: int) -> Optional[Entity]:
        ...

    async def update_status(self, user_id: int, is_active: bool) -> None:
        ...

    async def get_active_players_profiles(self, exclude_user_id: int, offset: int, limit: int, min_elo: Optional[int], max_elo: Optional[int], min_rating: Optional[float], role_ids: Optional[List[int]]): # <--- Обновить сигнатуру
        ...
    

class LFGStatusRepository:

    async def get_or_create(self, user_id: int):
        async with async_session_maker() as session:
            query = select(LFGStatus).where(LFGStatus.user_id == user_id)
            result = await session.execute(query)
            status = result.scalar_one_or_none()
            if not status:
                stmt = insert(LFGStatus).values(user_id=user_id, is_active=False).returning(LFGStatus)
                result = await session.execute(stmt)
                status = result.scalar_one()
                await session.commit()
            return status


    async def update_status(self, user_id: int, is_active: bool):
        async with async_session_maker() as session:
            stmt = update(LFGStatus).where(LFGStatus.user_id == user_id).values(is_active=is_active)
            await session.execute(stmt)
            await session.commit()


    async def get_active_players_profiles(
        self, 
        exclude_user_id: int, 
        offset: int, 
        limit: int,
        min_elo: Optional[int],
        max_elo: Optional[int],
        min_rating: Optional[float],
        role_ids: Optional[List[int]]
    ):
        async with async_session_maker() as session:
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
            
            result = await session.execute(query)
            return result.all()
