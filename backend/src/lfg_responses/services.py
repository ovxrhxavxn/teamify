from fastapi import HTTPException, status

from .repositories import LFGResponseRepository
from .schemas import ResponseNotification
from ..faceit.services import FaceitService
from ..websockets.dependencies import manager


COOLDOWN_MINUTES = 5


class LFGResponseService:
    def __init__(
        self,
        repo: LFGResponseRepository,
        faceit_service: FaceitService,
    ):
        self._repo = repo
        self._faceit = faceit_service

    async def respond_to_player(
        self, responder_id: int, target_user_id: int
    ) -> dict:
        if responder_id == target_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя откликнуться на самого себя",
            )

        recent = await self._repo.get_recent_response(
            responder_id, target_user_id, cooldown_minutes=COOLDOWN_MINUTES
        )
        if recent:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Можно откликнуться повторно через {COOLDOWN_MINUTES} мин",
            )

        response = await self._repo.create(responder_id, target_user_id)

        responder_faceit = await self._faceit.get_faceit_data_by_user_id(
            responder_id
        )
        if responder_faceit:
            faceit_profile_url = (
                f"https://www.faceit.com/en/players/{responder_faceit.nickname}"
            )
            notification = ResponseNotification(
                type="lfg_response",
                responder_nickname=responder_faceit.nickname,
                responder_avatar=responder_faceit.avatar,
                responder_faceit_url=faceit_profile_url,
                responder_elo=responder_faceit.elo,
                responder_lvl=responder_faceit.lvl,
                response_id=response.id,
            )
            await self._send_notification_to_user(
                target_user_id, notification.model_dump()
            )

        return {"status": "ok", "response_id": response.id}

    async def _send_notification_to_user(
        self, user_id: int, message: dict
    ):
        if user_id in manager.active_connections:
            connection = manager.active_connections[user_id]
            await connection.send_json(message)

