from typing import Protocol, List

from sqlalchemy import select, insert, func

from ..database.types.aliases import EntityId
from ..database.setup import async_session_maker
from .models import Review
from ..faceit.models import FaceitData
from ..users.models import User


class AbstractReviewsRepository[Entity](Protocol):

    async def add(self, schema: dict) -> EntityId:
        ...

    async def get_by_profile_id_with_author(self, profile_id: int, offset: int, limit: int) -> List[tuple]:
        ...

    async def get_average_rating_by_profile_id(self, profile_id: int) -> float:
        ...

    async def count_by_profile_id(self, profile_id: int) -> int:
        ...
    

class ReviewsRepository:

    model = Review

    async def add(self, schema: dict):
        async with async_session_maker() as session:
            stmt = insert(self.model).values(**schema).returning(self.model.id)
            result = await session.execute(stmt)
            await session.commit()

            return result.scalar_one()
        

    
    async def get_by_profile_id_with_author(self, profile_id: int, offset: int, limit: int):
        async with async_session_maker() as session:
            query = (
                select(
                    self.model,
                    FaceitData.nickname,
                    FaceitData.avatar
                )
                .join(User, self.model.author_id == User.id)
                .join(FaceitData, User.id == FaceitData.user_id)
                .where(self.model.profile_id == profile_id)
                .offset(offset)
                .limit(limit)
                .order_by(self.model.created_at.desc())
            )
            result = await session.execute(query)
            return result.all()
        

    async def get_average_rating_by_profile_id(self, profile_id: int) -> float:
        async with async_session_maker() as session:
            # Создаем запрос, который считает среднее значение (avg) поля rating
            query = select(func.avg(self.model.rating)).where(self.model.profile_id == profile_id)
            result = await session.execute(query)
            # scalar_one_or_none вернет среднее значение или None, если отзывов нет
            average_rating = result.scalar_one_or_none()
            # Если отзывов нет, возвращаем 0.0, иначе - посчитанное значение
            return float(average_rating) if average_rating is not None else 0.0
        

    async def count_by_profile_id(self, profile_id: int) -> int:
        async with async_session_maker() as session:
            # Запрос для подсчета записей
            query = select(func.count()).select_from(self.model).where(self.model.profile_id == profile_id)
            result = await session.execute(query)
            # scalar_one вернет одно значение (наше число)
            return result.scalar_one()