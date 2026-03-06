from datetime import datetime, timedelta

from sqlalchemy import insert, select, update

from ..database.repositories import BaseRepository
from .models import LFGResponse, ResponseStatus


class LFGResponseRepository(BaseRepository):

    async def create(self, responder_id: int, target_user_id: int) -> LFGResponse:
        stmt = (
            insert(LFGResponse)
            .values(
                responder_id=responder_id,
                target_user_id=target_user_id,
                status=ResponseStatus.PENDING,
            )
            .returning(LFGResponse)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def get_recent_response(
        self,
        responder_id: int,
        target_user_id: int,
        cooldown_minutes: int = 5,
    ) -> LFGResponse | None:
        cutoff = datetime.utcnow() - timedelta(minutes=cooldown_minutes)
        query = select(LFGResponse).where(
            LFGResponse.responder_id == responder_id,
            LFGResponse.target_user_id == target_user_id,
            LFGResponse.created_at >= cutoff,
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def update_status(
        self, response_id: int, new_status: ResponseStatus
    ) -> None:
        stmt = (
            update(LFGResponse)
            .where(LFGResponse.id == response_id)
            .values(status=new_status)
        )
        await self._session.execute(stmt)

    async def get_responses_for_user(
        self, user_id: int, offset: int = 0, limit: int = 20
    ):
        query = (
            select(LFGResponse)
            .where(LFGResponse.target_user_id == user_id)
            .order_by(LFGResponse.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self._session.execute(query)
        return result.scalars().all()
