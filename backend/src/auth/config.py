from ..config import BaseConfig


class JWTConfig(BaseConfig):
    JWT_SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRES: int = 60*24


jwt_config = JWTConfig()