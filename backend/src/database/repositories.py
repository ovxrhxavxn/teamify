from typing import Protocol


class SQLAlchemyRepository[Model](Protocol):
    model: Model = ...