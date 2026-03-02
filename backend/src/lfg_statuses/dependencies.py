# dependencies.py
from .services import LFGStatusService
from .repositories import LFGStatusRepository


def get_lfg_status_service() -> LFGStatusService:
    return LFGStatusService(LFGStatusRepository)
