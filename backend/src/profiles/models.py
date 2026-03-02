from typing import Optional, List
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database.setup import Base
from ..database.types.annotated_types import intpk


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    description: Mapped[Optional[str]]
