from cryptography.fernet import Fernet, InvalidToken

from .config import encryption_config


class EncryptionService:

    def __init__(self):
        self._key = encryption_config.FERNET_ENCRYPTION_KEY.encode()
        self.fernet = Fernet(self._key)

    def encrypt(self, data: str) -> str:
        """Шифрует строку и возвращает зашифрованную строку."""
        encrypted_data = self.fernet.encrypt(data.encode())
        return encrypted_data.decode()

    def decrypt(self, encrypted_data: str) -> str | None:
        """Расшифровывает строку и возвращает оригинал или None в случае ошибки."""
        try:
            decrypted_data = self.fernet.decrypt(encrypted_data.encode())
            return decrypted_data.decode()
        except InvalidToken:
            # Сюда попадем, если данные повреждены или ключ неверный
            return None