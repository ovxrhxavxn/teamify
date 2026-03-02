from ..config import BaseConfig


class FaceitConfig(BaseConfig):
    FACEIT_CLIENT_ID: str
    FACEIT_CLIENT_SECRET: str
    FACEIT_AUTH_ENDPOINT: str
    FACEIT_TOKEN_ENDPOINT: str
    FACEIT_USERINFO_ENDPOINT: str
    FACEIT_SERVER_API_KEY: str
    FACEIT_DATA_API_ENDPOINT: str
    FACEIT_CALLBACK_URI: str


faceit_config = FaceitConfig()