from datetime import timedelta, datetime, timezone

from jose import JWTError, jwt

from .config import jwt_config
from .schemas import TokenPayload


class JWTService:

    def __init__(self):
        self._secret_key = jwt_config.JWT_SECRET_KEY
        self._algorithm = jwt_config.JWT_ALGORITHM
        self._access_token_expires_minutes = jwt_config.ACCESS_TOKEN_EXPIRES

    
    def create_access_token(self, user_id: int) -> str:
        """
        Генерирует новый JWT access token.

        :param user_id: ID пользователя из НАШЕЙ базы данных.
        :return: Строка с закодированным JWT.
        """
        # Время, когда токен был создан
        issued_at = datetime.now(timezone.utc)
        # Время, когда токен станет невалидным
        expires_at = issued_at + timedelta(minutes=self._access_token_expires_minutes)

        data_to_encode = {
            "sub": str(user_id),
            "exp": expires_at,
            "iat": issued_at,
        }

        encoded_jwt = jwt.encode(
            claims=data_to_encode,
            key=self._secret_key,
            algorithm=self._algorithm
        )

        return encoded_jwt

    def verify_token(self, token: str) -> int | None:
        """
        Проверяет токен и возвращает ID пользователя, если токен валиден.

        :param token: JWT токен для проверки.
        :return: ID пользователя или None, если токен невалиден.
        """
        try:
            payload = jwt.decode(
                token=token,
                key=self._secret_key,
                algorithms=[self._algorithm]
            )

            # Валидируем payload с помощью Pydantic модели и извлекаем ID
            token_data = TokenPayload(**payload)
            return token_data.sub

        except JWTError:
            # - неверная подпись
            # - истек срок действия (ExpiredSignatureError)
            # - неверный формат
            return None