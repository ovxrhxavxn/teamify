from ..config import BaseConfig


class JWTConfig(BaseConfig):
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRES: int
    REFRESH_TOKEN_EXPIRES: int = 30  # дней


jwt_config = JWTConfig()