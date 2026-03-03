from typing import Annotated
from datetime import date

from sqlalchemy.orm import mapped_column
from sqlalchemy import func


intpk = Annotated[int, mapped_column(primary_key=True)]
utcnow = Annotated[date, mapped_column(server_default=func.current_date())]