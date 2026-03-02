from .services import EncryptionService


def get_encryption_service() -> EncryptionService:
    return EncryptionService()