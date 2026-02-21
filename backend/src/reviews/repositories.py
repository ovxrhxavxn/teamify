from typing import Protocol

from sqlalchemy import select, insert

from ..database.types.aliases import EntityId
from ..database.setup import async_session_maker
from .models import Review


class AbstractReviewsRepository[Entity](Protocol):

    async def add(self, schema: dict) -> EntityId:
        ...

    async def get_by_profile_id(self, profile_id: int, offset: int, limit: int) -> list[Entity]:
        ...
    

class ReviewsRepository:

    model = Review

    async def add(self, schema: dict):
        async with async_session_maker() as session:
            stmt = insert(self.model).values(**schema).returning(self.model.id)
            result = await session.execute(stmt)
            await session.commit()

            return result.scalar_one()
        

    async def get_by_user_id(self, profile_id: int, offset: int, limit: int):
        async with async_session_maker() as session:
            query = select(self.model).where(self.model.profile_id == profile_id).offset(offset).limit(limit)

            result = await session.execute(query)
            await session.commit()

            return result.scalars().all()