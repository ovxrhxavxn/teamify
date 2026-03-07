from pydantic_settings import SettingsConfigDict

from ..config import BaseConfig


class DBConfig(BaseConfig):
    host: str
    port: int
    name: str
    user: str
    password: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="DB_",
        extra="ignore",
    )


db_config = DBConfig()