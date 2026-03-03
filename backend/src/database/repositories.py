from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession


class SQLAlchemyRepository[Model](Protocol):
    model: Model = ...


class BaseRepository:

    def __init__(self, session: AsyncSession):
        self._session = session