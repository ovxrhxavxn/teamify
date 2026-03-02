from typing import Protocol

from sqlalchemy import select, insert, update

from ..database.types.aliases import EntityId
from ..database.setup import async_session_maker
from ..users.models import User


class AbstractUserRepository[Entity](Protocol):

    async def get(self, id: int) -> Entity:
        ...

    async def add(self, schema: dict) -> EntityId:
        ...

    async def update_rating(self, user_id: int, new_rating: float) -> None:
        ...



class UserRepository:

    model = User

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
        

    async def update_rating(self, user_id: int, new_rating: float):
        async with async_session_maker() as session:
            stmt = (
                update(self.model)
                .where(self.model.id == user_id)
                .values(rating=new_rating)
            )
            await session.execute(stmt)
            await session.commit()