from typing import Protocol

from aiohttp import ClientSession, BasicAuth, ClientError
from sqlalchemy import select, insert
from fastapi import HTTPException, status

from .config import faceit_config
from ..database.setup import async_session_maker
from .models import FaceitData, FaceitAuthData
from ..database.types.aliases import EntityId


class AbstractFaceitRepository[Entity](Protocol):

    async def get_token(self, code: str, code_verifier: str) -> dict:
       ...

    async def get_user_info(self, accsess_token: str) -> dict:
        ...

    async def get_faceit_data_by_guid(self, guid: str) -> Entity:
        ...

    async def add_faceit_auth_data(self, schema: dict) -> EntityId:
        ...

    async def get_player_stats(self, player_id: str) -> dict | None:
        ...

    async def add_faceit_data(self, schema: dict) -> EntityId:
        ...

    async def get_player_details(self, player_id: str) -> dict | None:
        ...

    async def get_faceit_data_by_user_id(self, user_id: int) -> Entity:
        ...



class FaceitRepository:

    async def get_player_details(self, player_id: str):
        """Получает общую информацию об игроке, включая ELO и уровень."""
        details_url = f"{faceit_config.FACEIT_DATA_API_ENDPOINT}/players/{player_id}"
        headers = {
            'Authorization': f'Bearer {faceit_config.FACEIT_SERVER_API_KEY}'
        }

        async with ClientSession() as session:
            try:
                async with session.get(url=details_url, headers=headers) as response:
                    response.raise_for_status()
                    details_data = await response.json()
                    return details_data
            except ClientError as e:
                print(f"Произошла ошибка при запросе деталей игрока {player_id}: {e}")
                return None
            
    
    async def get_token(self, code: str, code_verifier: str):
        auth = BasicAuth(login=faceit_config.FACEIT_CLIENT_ID, password=faceit_config.FACEIT_CLIENT_SECRET)
        payload = {
            'grant_type': 'authorization_code',
            'code': code,
            'code_verifier': code_verifier,
            'redirect_uri': faceit_config.FACEIT_CALLBACK_URI,
            'scope': 'openid profile'
        }
        
        async with ClientSession() as session:
            try:
                async with session.post(url=faceit_config.FACEIT_TOKEN_ENDPOINT, auth=auth, data=payload) as response:
                    # Проверяем статус ответа
                    if response.status != 200:
                        error_details = ""
                        # Пытаемся прочитать ответ как JSON, если это возможно
                        if 'application/json' in response.headers.get('Content-Type', ''):
                            error_data = await response.json()
                            error_details = error_data.get('error_description', str(error_data))
                        else:
                            # Если не JSON (как в нашем случае, с HTML), читаем как текст
                            error_details = await response.text()

                        print(f"ОШИБКА ОТ FACEIT API: Статус {response.status}, Детали: {error_details}")
                        
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Faceit API error: Unauthorized Client or Invalid Grant. Please check credentials."
                        )
                    
                    # Если все хорошо (статус 200), читаем JSON
                    token_data = await response.json()
                    return token_data
            except ClientError as e:
                # Отлавливаем ошибки соединения и т.д.
                print(f"Сетевая ошибка при запросе к Faceit API: {e}")
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Could not connect to Faceit API."
                )


    async def get_user_info(self, access_token: str):

        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        async with ClientSession() as session:
            try:
                # Делаем асинхронный GET-запрос
                async with session.get(url=faceit_config.FACEIT_USERINFO_ENDPOINT, headers=headers) as response:

                    # Проверяем, что запрос прошел успешно (код ответа 2xx)
                    response.raise_for_status()

                    # Асинхронно читаем ответ в формате JSON
                    user_data = await response.json()
                    return user_data

            except ClientError as e:
                # Обрабатываем возможные ошибки сети или невалидный токен
                print(f"Произошла ошибка при запросе информации о пользователе: {e}")
                return None
            

    async def get_faceit_data_by_guid(self, guid: str):

        async with async_session_maker() as session:

            query = select(FaceitData).where(FaceitData.player_id == guid)

            result = await session.execute(query)
            await session.commit()

            return result.scalar_one_or_none() 
        

    async def add_faceit_auth_data(self, schema: dict):
        async with async_session_maker() as session:

            stmt = insert(FaceitAuthData).values(**schema).returning(FaceitAuthData.id)

            result = await session.execute(stmt)
            await session.commit()

            return result.scalar_one()
        

    async def get_player_stats(self, player_id: str):
        """Получает игровую статистику по ID игрока с помощью серверного API ключа."""
        stats_url = f"{faceit_config.FACEIT_DATA_API_ENDPOINT}/players/{player_id}/stats/cs2"
        headers = {
            # ВАЖНО: здесь используется серверный API ключ, а не токен пользователя!
            'Authorization': f'Bearer {faceit_config.FACEIT_SERVER_API_KEY}'
        }
        async with ClientSession() as session:
            try:
                async with session.get(url=stats_url, headers=headers) as response:
                    response.raise_for_status()
                    stats_data = await response.json()
                    # У Faceit API есть особенность: если статистики по игре нет,
                    # он может вернуть 200 ОК с ошибкой в теле.
                    if "errors" in stats_data:
                         print(f"API Faceit вернуло ошибку для {player_id}: {stats_data['errors']}")
                         return None
                    return stats_data
            except ClientError as e:
                print(f"Произошла ошибка при запросе статистики для {player_id}: {e}")
                return None
            

    async def add_faceit_data(self, schema: dict):
        async with async_session_maker() as session:
            stmt = insert(FaceitData).values(**schema).returning(FaceitData.id)
            result = await session.execute(stmt)
            await session.commit()
            return result.scalar_one()
        

    async def get_faceit_data_by_user_id(self, user_id: int):
        async with async_session_maker() as session:
            query = select(FaceitData).where(FaceitData.user_id == user_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()