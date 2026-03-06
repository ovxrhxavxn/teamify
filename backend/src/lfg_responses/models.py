from datetime import datetime
import enum

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, Enum as SAEnum, func

from ..database.setup import Base
from ..database.types.annotated_types import intpk


class ResponseStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"


class LFGResponse(Base):
    __tablename__ = "lfg_responses"

    id: Mapped[intpk]
    responder_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    target_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[ResponseStatus] = mapped_column(
        SAEnum(ResponseStatus), default=ResponseStatus.PENDING
    )
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now()
    )
