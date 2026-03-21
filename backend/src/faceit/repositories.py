import logging
from aiohttp import ClientSession, BasicAuth, ClientError
from sqlalchemy import select, insert, update
from fastapi import HTTPException, status

from ..database.repositories import BaseRepository
from .config import faceit_config
from .models import FaceitData, FaceitAuthData

logger = logging.getLogger(__name__)


class FaceitAPIClient:
    async def get_token(self, code: str, code_verifier: str) -> dict:
        auth = BasicAuth(
            login=faceit_config.FACEIT_CLIENT_ID,
            password=faceit_config.FACEIT_CLIENT_SECRET,
        )
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "code_verifier": code_verifier,
            "redirect_uri": faceit_config.FACEIT_CALLBACK_URI,
            "scope": "openid profile",
        }
        async with ClientSession() as session:
            try:
                async with session.post(
                    url=faceit_config.FACEIT_TOKEN_ENDPOINT,
                    auth=auth,
                    data=payload,
                ) as response:
                    if response.status != 200:
                        error_details = await response.text()
                        logger.error(
                            "Faceit token error: status=%s details=%s",
                            response.status,
                            error_details,
                        )
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Faceit API error: Unauthorized Client or Invalid Grant.",
                        )
                    return await response.json()
            except ClientError as e:
                logger.error("Network error requesting Faceit token: %s", e)
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Could not connect to Faceit API.",
                )

    async def get_user_info(self, access_token: str) -> dict | None:
        headers = {"Authorization": f"Bearer {access_token}"}
        async with ClientSession() as session:
            try:
                async with session.get(
                    url=faceit_config.FACEIT_USERINFO_ENDPOINT,
                    headers=headers,
                ) as response:
                    response.raise_for_status()
                    return await response.json()
            except ClientError as e:
                logger.error("Error fetching user info: %s", e)
                return None

    async def get_player_details(self, player_id: str) -> dict | None:
        url = f"{faceit_config.FACEIT_DATA_API_ENDPOINT}/players/{player_id}"
        headers = {"Authorization": f"Bearer {faceit_config.FACEIT_SERVER_API_KEY}"}
        async with ClientSession() as session:
            try:
                async with session.get(url=url, headers=headers) as response:
                    response.raise_for_status()
                    return await response.json()
            except ClientError as e:
                logger.error("Error fetching player details %s: %s", player_id, e)
                return None

    async def get_player_stats(self, player_id: str) -> dict | None:
        url = f"{faceit_config.FACEIT_DATA_API_ENDPOINT}/players/{player_id}/stats/cs2"
        headers = {"Authorization": f"Bearer {faceit_config.FACEIT_SERVER_API_KEY}"}
        async with ClientSession() as session:
            try:
                async with session.get(url=url, headers=headers) as response:
                    response.raise_for_status()
                    data = await response.json()
                    if "errors" in data:
                        logger.warning(
                            "Faceit stats errors for %s: %s",
                            player_id,
                            data["errors"],
                        )
                        return None
                    return data
            except ClientError as e:
                logger.error("Error fetching stats for %s: %s", player_id, e)
                return None


class FaceitRepository(BaseRepository):
    async def get_faceit_data_by_guid(self, guid: str) -> FaceitData | None:
        query = select(FaceitData).where(FaceitData.player_id == guid)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_faceit_data_by_user_id(self, user_id: int) -> FaceitData | None:
        query = select(FaceitData).where(FaceitData.user_id == user_id)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def add_faceit_auth_data(self, schema: dict) -> int:
        stmt = insert(FaceitAuthData).values(**schema).returning(FaceitAuthData.id)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def update_faceit_auth_data(
        self, user_id: int, encrypted_refresh_token: str
    ) -> None:
        stmt = (
            update(FaceitAuthData)
            .where(FaceitAuthData.user_id == user_id)
            .values(encrypted_refresh_token=encrypted_refresh_token)
        )
        await self._session.execute(stmt)

    async def add_faceit_data(self, schema: dict) -> int:
        stmt = insert(FaceitData).values(**schema).returning(FaceitData.id)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def update_faceit_data(self, user_id: int, schema: dict) -> None:
        stmt = (
            update(FaceitData)
            .where(FaceitData.user_id == user_id)
            .values(**schema)
        )
        await self._session.execute(stmt)

