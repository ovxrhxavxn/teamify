from typing import Protocol, List

from sqlalchemy import insert, select, update
from sqlalchemy.orm import selectinload


from ..database.types.aliases import EntityId
from ..database.setup import async_session_maker
from .models import Profile, GameRole, profile_roles_association


class AbstractProfileRepository[Entity](Protocol):
    async def add(self, schema: dict) -> EntityId:
        ...
    async def get_by_user_id(self, user_id: int) -> Entity:
        ...
    async def update_by_user_id(self, user_id: int, data: dict) -> Entity | None:
        ...
    async def get(self, id: int) -> Entity | None:
        ...
    async def get_all_roles(self) -> List[Entity]:
        ...


class ProfileRepository:

    model = Profile


    async def get(self, id: int):
        async with async_session_maker() as session:
            query = select(self.model).where(self.model.id == id).options(selectinload(self.model.roles))
            result = await session.execute(query)
            return result.scalar_one_or_none()
        

    async def add(self, schema: dict):
        async with async_session_maker() as session:
            stmt = insert(self.model).values(**schema).returning(self.model.id)
            result = await session.execute(stmt)
            await session.commit()
            return result.scalar_one()
        

    async def get_by_user_id(self, user_id: int):
         async with async_session_maker() as session:
            query = select(self.model).where(self.model.user_id == user_id).options(selectinload(self.model.roles))
            result = await session.execute(query)
            return result.scalar_one_or_none()
         

    async def update_by_user_id(self, user_id: int, data: dict):
        async with async_session_maker() as session:
            profile_query = select(self.model).where(self.model.user_id == user_id)
            profile_result = await session.execute(profile_query)
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
                await session.execute(stmt)

            if "role_ids" in data:
                # 1. Находим объекты ролей по их ID
                roles_query = select(GameRole).where(GameRole.id.in_(data["role_ids"]))
                roles_result = await session.execute(roles_query)
                roles_to_set = roles_result.scalars().all()

                profile_to_update.roles = roles_to_set

            await session.commit()
            
            updated_profile = await self.get_by_user_id(user_id)
            return updated_profile
        

    async def get_all_roles(self):
        async with async_session_maker() as session:
            query = select(GameRole).order_by(GameRole.id)
            result = await session.execute(query)
            return result.scalars().all()

