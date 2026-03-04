from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from ..database.setup import Base
from ..database.types.annotated_types import intpk


class FaceitData(Base):
    __tablename__ = "faceit_data"

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    player_id: Mapped[str] = mapped_column(unique=True)
    nickname: Mapped[str] = mapped_column(unique=True)
    elo: Mapped[int] = mapped_column()
    lvl: Mapped[int] = mapped_column()
    k_d_ratio: Mapped[float] = mapped_column()
    k_r_ratio: Mapped[float] = mapped_column(default=0.0)
    avg_damage_per_round: Mapped[float] = mapped_column()
    matches: Mapped[int] = mapped_column()
    win_rate_percentage: Mapped[float] = mapped_column()
    average_headshots_percentage: Mapped[int] = mapped_column()
    longest_win_streak: Mapped[int] = mapped_column(default=0)
    avatar: Mapped[Optional[str]]


class FaceitAuthData(Base):
    __tablename__ = "faceit_auth_data"

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    encrypted_refresh_token: Mapped[str] = mapped_column()
