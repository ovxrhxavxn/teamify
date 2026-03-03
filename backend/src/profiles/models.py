from typing import Optional, List
from sqlalchemy import Table, Column, Integer, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database.setup import Base
from ..database.types.annotated_types import intpk


profile_roles_association = Table(
    "profile_roles",
    Base.metadata,
    Column("profile_id", Integer, ForeignKey("profiles.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("game_roles.id"), primary_key=True),
)


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    description: Mapped[Optional[str]]

    roles: Mapped[List["GameRole"]] = relationship(
        secondary=profile_roles_association,
        back_populates=None,
        lazy="selectin"
    )

# --- НОВАЯ МОДЕЛЬ ---
class GameRole(Base):
    __tablename__ = "game_roles"
    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(String(50), unique=True)