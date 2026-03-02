from ..config import BaseConfig


class EncryptionConfig(BaseConfig):
    FERNET_ENCRYPTION_KEY: str


encryption_config = EncryptionConfig()