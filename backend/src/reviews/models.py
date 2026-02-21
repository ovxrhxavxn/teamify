from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey

from ..database.setup import Base
from ..database.types.annotated_types import intpk, utcnow


class Review(Base):

    __tablename__ = "reviews"

    id: Mapped[intpk]
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"))
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    content: Mapped[str] = mapped_column()
    rating: Mapped[int] = mapped_column()
    created_at: Mapped[utcnow]