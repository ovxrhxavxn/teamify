import asyncio
import logging

from .repositories import FaceitAPIClient, FaceitRepository
from .schemas import (
    FaceitTokenResponse,
    FaceitUserInfoResponse,
    FaceitDataFromDB,
    FaceitAuthData,
    FaceitPlayerStatsResponse,
    FaceitData,
    FaceitPlayerDetailsResponse,
    FaceitCallbackPayload,
)
from ..profiles.schemas import Profile
from ..profiles.repositories import ProfileRepository
from ..users.schemas import User as UserSchema
from ..users.repositories import UserRepository
from ..encryption.services import EncryptionService
from ..auth.services import JWTService

logger = logging.getLogger(__name__)


class FaceitService:
    def __init__(
        self,
        repo: FaceitRepository,
        api_client: FaceitAPIClient,
    ):
        self._repo = repo
        self._api = api_client

    async def get_token(self, code: str, code_verifier: str) -> FaceitTokenResponse:
        data = await self._api.get_token(code, code_verifier)
        return FaceitTokenResponse.model_validate(data)

    async def get_user_info(self, access_token: str) -> FaceitUserInfoResponse:
        data = await self._api.get_user_info(access_token)
        return FaceitUserInfoResponse.model_validate(data)

    async def get_player_stats(self, player_id: str) -> FaceitPlayerStatsResponse | None:
        data = await self._api.get_player_stats(player_id)
        if not data:
            return None
        lifetime_stats = data.get("lifetime", {})
        return FaceitPlayerStatsResponse.model_validate(lifetime_stats)

    async def get_player_details(self, player_id: str) -> FaceitPlayerDetailsResponse | None:
        data = await self._api.get_player_details(player_id)
        if not data:
            return None
        return FaceitPlayerDetailsResponse.model_validate(data)

    async def get_faceit_data_by_guid(self, guid: str) -> FaceitDataFromDB | None:
        faceit_data = await self._repo.get_faceit_data_by_guid(guid)
        if faceit_data:
            return FaceitDataFromDB.model_validate(faceit_data)
        return None

    async def get_faceit_data_by_user_id(self, user_id: int) -> FaceitDataFromDB | None:
        faceit_data = await self._repo.get_faceit_data_by_user_id(user_id)
        if faceit_data:
            return FaceitDataFromDB.model_validate(faceit_data)
        return None

    async def add_faceit_auth_data(self, schema: FaceitAuthData) -> int:
        return await self._repo.add_faceit_auth_data(schema.model_dump())

    async def update_faceit_auth_data(
        self, user_id: int, encrypted_refresh_token: str
    ) -> None:
        await self._repo.update_faceit_auth_data(user_id, encrypted_refresh_token)

    async def add_faceit_data(self, schema: FaceitData) -> int:
        return await self._repo.add_faceit_data(schema.model_dump())


class FaceitAuthService:
    def __init__(
        self,
        faceit_service: FaceitService,
        user_repo: UserRepository,
        profile_repo: ProfileRepository,
        encryption_service: EncryptionService,
        jwt_service: JWTService,
    ):
        self._faceit = faceit_service
        self._user_repo = user_repo
        self._profile_repo = profile_repo
        self._encryption = encryption_service
        self._jwt = jwt_service

    async def handle_callback(
        self, payload: FaceitCallbackPayload
    ) -> tuple[str, str]:
        """
        Возвращает (access_token, refresh_token) нашего приложения.
        """
        token_response = await self._faceit.get_token(
            code=payload.code,
            code_verifier=payload.code_verifier,
        )

        user_info = await self._faceit.get_user_info(token_response.access_token)
        player_guid = user_info.guid

        existing = await self._faceit.get_faceit_data_by_guid(player_guid)

        if existing:
            logger.info("Existing user %s logged in.", existing.nickname)
            user_id = existing.user_id
            # Обновляем Faceit refresh token в БД
            encrypted_token = self._encryption.encrypt(token_response.refresh_token)
            await self._faceit.update_faceit_auth_data(user_id, encrypted_token)
        else:
            user_id = await self._register_new_user(
                player_guid=player_guid,
                nickname=user_info.nickname,
                refresh_token=token_response.refresh_token,
            )

        access_token = self._jwt.create_access_token(user_id=user_id)
        refresh_token = self._jwt.create_refresh_token(user_id=user_id)
        return access_token, refresh_token

    async def _register_new_user(
        self,
        player_guid: str,
        nickname: str,
        refresh_token: str,
    ) -> int:
        new_user = UserSchema(rating=0)
        user_id = await self._user_repo.add(new_user.model_dump(exclude_none=True))

        new_profile = Profile(user_id=user_id)
        await self._profile_repo.add(new_profile.model_dump(exclude_none=True))

        encrypted_token = self._encryption.encrypt(refresh_token)
        auth_data = FaceitAuthData(
            user_id=user_id, encrypted_refresh_token=encrypted_token
        )
        await self._faceit.add_faceit_auth_data(auth_data)

        stats, details = await asyncio.gather(
            self._faceit.get_player_stats(player_guid),
            self._faceit.get_player_details(player_guid),
        )

        faceit_data = self._build_faceit_data(
            user_id=user_id,
            player_guid=player_guid,
            nickname=nickname,
            stats=stats,
            details=details,
        )
        await self._faceit.add_faceit_data(faceit_data)

        return user_id

    @staticmethod
    def _build_faceit_data(
        user_id: int,
        player_guid: str,
        nickname: str,
        stats: FaceitPlayerStatsResponse | None,
        details: FaceitPlayerDetailsResponse | None,
    ) -> FaceitData:
        k_d = float(stats.k_d_ratio) if stats and stats.k_d_ratio else 0.0
        k_r = float(stats.k_r_ratio) if stats and stats.k_r_ratio else 0.0
        adr = (
            float(stats.avg_damage_per_round)
            if stats and stats.avg_damage_per_round
            else 0.0
        )
        matches = int(stats.matches) if stats and stats.matches else 0
        win_rate_str = (
            stats.win_rate_percentage.replace("%", "")
            if stats and stats.win_rate_percentage
            else "0"
        )
        win_rate = float(win_rate_str)
        headshots_str = (
            stats.average_headshots_percentage.replace("%", "")
            if stats and stats.average_headshots_percentage
            else "0"
        )
        headshots = int(headshots_str)
        longest_win_streak = (
            int(stats.longest_win_streak)
            if stats and stats.longest_win_streak
            else 0
        )

        elo = details.games.cs2.faceit_elo if details and details.games.cs2 else 0
        lvl = details.games.cs2.skill_level if details and details.games.cs2 else 0
        avatar_url = str(details.avatar) if details and details.avatar else None

        return FaceitData(
            user_id=user_id,
            player_id=player_guid,
            nickname=nickname,
            elo=elo,
            lvl=lvl,
            k_d_ratio=k_d,
            k_r_ratio=k_r,
            avg_damage_per_round=adr,
            matches=matches,
            win_rate_percentage=win_rate,
            average_headshots_percentage=headshots,
            longest_win_streak=longest_win_streak,
            avatar=avatar_url,
        )
