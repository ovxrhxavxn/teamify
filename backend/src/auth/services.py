from datetime import timedelta, datetime, timezone
from jose import JWTError, jwt
from .config import jwt_config
from .schemas import TokenPayload


class JWTService:
    def __init__(self):
        self._secret_key = jwt_config.JWT_SECRET_KEY
        self._algorithm = jwt_config.JWT_ALGORITHM
        self._access_token_expires_minutes = jwt_config.ACCESS_TOKEN_EXPIRES
        self._refresh_token_expires_days = jwt_config.REFRESH_TOKEN_EXPIRES

    def create_access_token(self, user_id: int) -> str:
        issued_at = datetime.now(timezone.utc)
        expires_at = issued_at + timedelta(minutes=self._access_token_expires_minutes)
        data_to_encode = {
            "sub": str(user_id),
            "exp": expires_at,
            "iat": issued_at,
            "type": "access",
        }
        return jwt.encode(data_to_encode, self._secret_key, self._algorithm)

    def create_refresh_token(self, user_id: int) -> str:
        issued_at = datetime.now(timezone.utc)
        expires_at = issued_at + timedelta(days=self._refresh_token_expires_days)
        data_to_encode = {
            "sub": str(user_id),
            "exp": expires_at,
            "iat": issued_at,
            "type": "refresh",
        }
        return jwt.encode(data_to_encode, self._secret_key, self._algorithm)

    def verify_token(self, token: str) -> int | None:
        """Проверяет access token."""
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
            # Разрешаем старые токены без type и новые с type="access"
            token_type = payload.get("type")
            if token_type is not None and token_type != "access":
                return None
            token_data = TokenPayload(**payload)
            return token_data.sub
        except JWTError:
            return None

    def verify_refresh_token(self, token: str) -> int | None:
        """Проверяет refresh token."""
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
            if payload.get("type") != "refresh":
                return None
            return int(payload["sub"])
        except JWTError:
            return None
