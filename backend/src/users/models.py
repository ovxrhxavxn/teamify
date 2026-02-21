from sqlalchemy.orm import Mapped, mapped_column

from ..database.setup import Base
from ..database.types.annotated_types import intpk, utcnow


class User(Base):

    __tablename__ = "users"

    id: Mapped[intpk]
    registration_date: Mapped[utcnow]
    rating: Mapped[float] = mapped_column()