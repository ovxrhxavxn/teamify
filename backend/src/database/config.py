from ..config import BaseConfig


class DBConfig(BaseConfig):
    host: str
    port: int
    db_name: str
    user: str
    password: str


db_config = DBConfig()