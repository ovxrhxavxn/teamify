from .services import JWTService


def get_jwt_service() -> JWTService:
    return JWTService()