from typing import Protocol

from sqlalchemy import insert, select, update

from ..database.types.aliases import EntityId
from ..database.setup import async_session_maker
from .models import Profile


class AbstractProfileRepository[Entity](Protocol):
    async def add(self, schema: dict) -> EntityId:
        ...
    async def get_by_user_id(self, user_id: int) -> Entity:
        ...
    async def update_by_user_id(self, user_id: int, data: dict) -> Entity | None:
        ...
    async def get(self, id: int) -> Entity | None:

        ...
class ProfileRepository:

    model = Profile


    async def get(self, id: int):
        async with async_session_maker() as session:
            query = select(self.model).where(self.model.id == id)
            result = await session.execute(query)
            return result.scalar_one_or_none()
        

    async def add(self, schema: dict):
        async with async_session_maker() as session:
            stmt = insert(self.model).values(**schema).returning(self.model.id)
            result = await session.execute(stmt)
            await session.commit()
            return result.scalar_one()
        

    async def get_by_user_id(self, user_id: int):
         async with async_session_maker() as session:
            query = select(self.model).where(self.model.user_id == user_id)
            result = await session.execute(query)
            await session.commit()
            return result.scalar_one()
         

    async def update_by_user_id(self, user_id: int, data: dict):
        async with async_session_maker() as session:
            stmt = (
                update(self.model)
                .where(self.model.user_id == user_id)
                .values(**data)
                .returning(self.model)
            )
            result = await session.execute(stmt)
            await session.commit()
            return result.scalar_one_or_none()
