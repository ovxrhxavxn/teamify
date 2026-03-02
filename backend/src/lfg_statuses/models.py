from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey

from ..database.setup import Base
from ..database.types.annotated_types import intpk


class LFGStatus(Base):
    __tablename__ = "lfg_statuses"

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    is_active: Mapped[bool] = mapped_column(default=False)