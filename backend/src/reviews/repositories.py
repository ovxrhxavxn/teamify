from typing import List

from sqlalchemy import select, insert, func

from ..database.repositories import BaseRepository
from .models import Review
from ..faceit.models import FaceitData
from ..users.models import User


class ReviewsRepository(BaseRepository):
    model = Review

    async def add(self, schema: dict) -> int:
        stmt = insert(self.model).values(**schema).returning(self.model.id)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def get_by_profile_id_with_author(
        self,
        profile_id: int,
        offset: int,
        limit: int,
    ) -> List[tuple]:
        query = (
            select(self.model, FaceitData.nickname, FaceitData.avatar)
            .join(User, self.model.author_id == User.id)
            .join(FaceitData, User.id == FaceitData.user_id)
            .where(self.model.profile_id == profile_id)
            .order_by(self.model.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self._session.execute(query)
        return list(result.all())

    async def get_average_rating_by_profile_id(self, profile_id: int) -> float:
        query = select(func.avg(self.model.rating)).where(
            self.model.profile_id == profile_id
        )
        result = await self._session.execute(query)
        average_rating = result.scalar_one_or_none()
        return float(average_rating) if average_rating is not None else 0.0

    async def count_by_profile_id(self, profile_id: int) -> int:
        query = (
            select(func.count())
            .select_from(self.model)
            .where(self.model.profile_id == profile_id)
        )
        result = await self._session.execute(query)
        return result.scalar_one()