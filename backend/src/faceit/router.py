import asyncio
from typing import Annotated

from fastapi import APIRouter, Depends

from ..auth.dependencies import get_jwt_service
from ..auth.services import JWTService
from ..users.services import UserService
from ..users.schemas import User
from ..users.dependencies import get_user_service
from ..faceit.services import FaceitService
from ..faceit.dependencies import get_faceit_service
from ..faceit.schemas import FaceitAuthData
from ..profiles.services import ProfileService
from ..profiles.dependencies import get_profile_service
from ..profiles.schemas import Profile
from ..encryption.services import EncryptionService
from ..encryption.dependencoes import get_encryption_service
from .schemas import (
    FaceitAuthData, 
    FaceitData, 
    AppTokenResponse, 
    FaceitCallbackPayload
)


router = APIRouter(prefix="/faceit", tags=["Faceit"])


@router.post("/oauth2/callback", response_model=AppTokenResponse)
async def faceit_auth_callback(
    payload: FaceitCallbackPayload,
    jwt_service: Annotated[JWTService, Depends(get_jwt_service)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    faceit_service: Annotated[FaceitService, Depends(get_faceit_service)],
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
    encryption_service: Annotated[EncryptionService, Depends(get_encryption_service)]
):
    
    faceit_token_response = await faceit_service.get_token(
        code=payload.code, 
        code_verifier=payload.code_verifier
    )
    
    user_info_response = await faceit_service.get_user_info(faceit_token_response.access_token)

    player_guid = user_info_response.guid
    user_id_for_jwt: int

    existing_faceit_data = await faceit_service.get_faceit_data_by_guid(player_guid)

    if not existing_faceit_data:
        # --- СЦЕНАРИЙ: НОВЫЙ ПОЛЬЗОВАТЕЛЬ ---

        new_user = User(rating=0)
        user_id_for_jwt = await user_service.add(new_user)

        new_profile = Profile(user_id=user_id_for_jwt)
        await profile_service.add(new_profile)

        encrypted_token = encryption_service.encrypt(faceit_token_response.refresh_token)
        auth_data = FaceitAuthData(user_id=user_id_for_jwt, encrypted_refresh_token=encrypted_token)
        await faceit_service.add_faceit_auth_data(auth_data)

        stats_task = faceit_service.get_player_stats(player_guid)
        details_task = faceit_service.get_player_details(player_guid)

        results = await asyncio.gather(stats_task, details_task)
        stats, details = results[0], results[1]
        
        # Безопасно извлекаем K/D и ADR
        k_d = float(stats.k_d_ratio) if stats and stats.k_d_ratio else 0.0
        adr = float(stats.avg_damage_per_round) if stats and stats.avg_damage_per_round else 0.0
        elo = details.games.cs2.faceit_elo if details and details.games.cs2 else 0
        lvl = details.games.cs2.skill_level if details and details.games.cs2 else 0
        
        # Новые поля
        matches = int(stats.matches) if stats and stats.matches else 0
        
        # Win Rate приходит как "58%", убираем "%" и конвертируем
        win_rate_str = stats.win_rate_percentage.replace('%', '') if stats and stats.win_rate_percentage else "0"
        win_rate = float(win_rate_str)
        
        headshots_str = stats.average_headshots_percentage.replace('%', '') if stats and stats.average_headshots_percentage else "0"
        headshots = int(headshots_str)

        avatar_url = str(details.avatar) if details and details.avatar else None

        faceit_data_to_add = FaceitData(
            user_id=user_id_for_jwt,
            player_id=player_guid,
            nickname=user_info_response.nickname,
            elo=elo,
            lvl=lvl,
            k_d_ratio=k_d,
            avg_damage_per_round=adr,
            matches=matches,
            win_rate_percentage=win_rate,
            average_headshots_percentage=headshots,
            avatar=avatar_url # <--- Передаем сюда либо URL, либо None
        )
        await faceit_service.add_faceit_data(faceit_data_to_add)

    else:
        # --- СЦЕНАРИЙ: СУЩЕСТВУЮЩИЙ ПОЛЬЗОВАТЕЛЬ ---

        user_id_for_jwt = existing_faceit_data.user_id

        # 2. Обновляем его данные (TODO: вынести в update-методы сервисов)
        # Например, можно обновить refresh_token, никнейм и пересчитать статистику
        print(f"Пользователь {existing_faceit_data.nickname} снова вошел в систему.")
        # await faceit_service.update_stats(user_id_for_jwt, player_guid)
        # await faceit_service.update_refresh_token(user_id_for_jwt, faceit_token_response.refresh_token)

    # --- ФИНАЛЬНЫЙ ШАГ: Генерируем и возвращаем наш JWT ---
    app_access_token = jwt_service.create_access_token(user_id=user_id_for_jwt)
    return AppTokenResponse(access_token=app_access_token)