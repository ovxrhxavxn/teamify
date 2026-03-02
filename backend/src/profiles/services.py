from .repositories import AbstractProfileRepository
from .schemas import Profile as ProfileSchema, ProfileFromDB, ProfileUpdate
from .models import Profile


class ProfileService:

    def __init__(self, repo: type[AbstractProfileRepository[Profile]]):
        self._repo = repo()

    async def get_by_id(self, profile_id: int):
        profile = await self._repo.get(profile_id)
        if profile:
            return ProfileFromDB.model_validate(profile)
        return None
    # ------------------------------------
    async def add(self, schema: ProfileSchema):
        profile_id = await self._repo.add(schema.model_dump(exclude_none=True))
        return profile_id
    
    async def get_by_user_id(self, user_id: int):
        profile = await self._repo.get_by_user_id(user_id)
        if profile:
            return ProfileFromDB.model_validate(profile)
        return None
    
    async def update_by_user_id(self, user_id: int, schema: ProfileUpdate):
        # Используем exclude_unset=True, чтобы обновлять только переданные поля
        data_to_update = schema.model_dump(exclude_unset=True)
        if not data_to_update:
            return None # Нечего обновлять
        updated_profile = await self._repo.update_by_user_id(user_id, data_to_update)
        if updated_profile:
            return ProfileFromDB.model_validate(updated_profile)
        return None
