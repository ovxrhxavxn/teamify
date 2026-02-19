from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey

from ..database.setup import Base
from ..database.annotated_types import intpk


class GameRole(Base):

    __tablename__ = "game_roles"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(unique=True)


class FaceitData(Base):

    __tablename__ = "faceit_data"

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    player_id: Mapped[str] = mapped_column(unique=True)
    nickname: Mapped[str] = mapped_column(unique=True)
    elo: Mapped[int] = mapped_column()
    lvl: Mapped[int] = mapped_column()
    k_d_ratio: Mapped[float] = mapped_column()
    avg_kills: Mapped[float] = mapped_column()


class FaceitAuthData(Base):

    __tablename__ = "faceit_auth_data"

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    refresh_token: Mapped[str] = mapped_column()