from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey

from ..database.setup import Base
from database.types.annotated_types import intpk


class Profile(Base):

    __tablename__ = "profiles"

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    description: Mapped[str] = mapped_column()