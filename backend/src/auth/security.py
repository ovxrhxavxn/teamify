from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from .dependencies import get_jwt_service
from .services import JWTService
from ..users.dependencies import get_user_service
from ..users.services import UserService
from ..users.schemas import UserFromDB


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    jwt_service: Annotated[JWTService, Depends(get_jwt_service)],
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> UserFromDB:
    """
    Зависимость для получения текущего пользователя по JWT токену.
    Проверяет токен и возвращает модель пользователя из БД.
    Если токен невалиден - выбрасывает ошибку 401.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id = jwt_service.verify_token(token)

    if user_id is None:
        raise credentials_exception

    user = await user_service.get(user_id)

    if user is None:
        raise credentials_exception

    return user