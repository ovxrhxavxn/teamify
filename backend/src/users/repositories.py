from typing import Protocol

from sqlalchemy import select, insert

from ..database.types import EntityId
from ..database.setup import async_session_maker
from ..users.models import User


class AbstractUserRepository[Entity](Protocol):

    async def get(self, id: int) -> Entity:
        ...

    async def add(self, schema: dict) -> EntityId:
        ...



class UserRepository:

    model = User

    async def get(self, id: int):
        async with async_session_maker() as session:
            query = select(self.model).where(self.model.id == id)
            result = await session.execute(query)

            return result.one_or_none()
        

    async def add(self, schema: dict): 
        async with async_session_maker() as session:
            stmt = insert(self.model).values(**schema).returning(self.model.id)
            result = await session.execute(stmt)
            await session.commit()

            return result.one_or_none()