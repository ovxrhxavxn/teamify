from typing import List

from sqlalchemy import insert, select, update
from sqlalchemy.orm import selectinload

from ..database.repositories import BaseRepository
from .models import Profile, GameRole


class ProfileRepository(BaseRepository):
    model = Profile

    async def get(self, profile_id: int) -> Profile | None:
        query = (
            select(self.model)
            .where(self.model.id == profile_id)
            .options(selectinload(self.model.roles))
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def add(self, schema: dict) -> int:
        stmt = insert(self.model).values(**schema).returning(self.model.id)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def get_by_user_id(self, user_id: int) -> Profile | None:
        query = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .options(selectinload(self.model.roles))
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def update_by_user_id(self, user_id: int, data: dict) -> Profile | None:
        profile_query = select(self.model).where(self.model.user_id == user_id)
        profile_result = await self._session.execute(profile_query)
        profile_to_update = profile_result.scalar_one_or_none()

        if not profile_to_update:
            return None

        update_data = {}
        if "description" in data:
            update_data["description"] = data["description"]

        if update_data:
            stmt = (
                update(self.model)
                .where(self.model.user_id == user_id)
                .values(**update_data)
            )
            await self._session.execute(stmt)

        if "role_ids" in data:
            roles_query = select(GameRole).where(GameRole.id.in_(data["role_ids"]))
            roles_result = await self._session.execute(roles_query)
            profile_to_update.roles = roles_result.scalars().all()

        await self._session.flush()
        return await self.get_by_user_id(user_id)


    async def get_all_roles(self) -> List[GameRole]:
        query = select(GameRole).order_by(GameRole.id)
        result = await self._session.execute(query)
        return list(result.scalars().all())
