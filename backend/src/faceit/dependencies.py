from .services import FaceitService
from .repositories import FaceitRepository


def get_faceit_service() -> FaceitService:
    return FaceitService(FaceitRepository)