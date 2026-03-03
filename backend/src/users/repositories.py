from sqlalchemy import select, insert, update

from ..database.repositories import BaseRepository
from .models import User


class UserRepository(BaseRepository):
    model = User

    async def get(self, user_id: int) -> User | None:
        query = select(self.model).where(self.model.id == user_id)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def add(self, schema: dict) -> int:
        stmt = insert(self.model).values(**schema).returning(self.model.id)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def update_rating(self, user_id: int, new_rating: float) -> None:
        stmt = (
            update(self.model)
            .where(self.model.id == user_id)
            .values(rating=new_rating)
        )
        await self._session.execute(stmt)