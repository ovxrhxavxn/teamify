from ..config import BaseConfig


class FaceitConfig(BaseConfig):
    FACEIT_CLIENT_ID: str
    FACEIT_CLIENT_SECRET: str
    FACEIT_AUTH_ENDPOINT: str
    FACEIT_TOKEN_ENDPOINT: str


faceit_config = FaceitConfig()