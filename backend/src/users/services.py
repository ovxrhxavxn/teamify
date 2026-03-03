from .repositories import UserRepository
from .schemas import UserFromDB, User as UserSchema


class UserService:
    def __init__(self, repo: UserRepository):
        self._repo = repo

    async def add(self, schema: UserSchema) -> int:
        return await self._repo.add(schema.model_dump(exclude_none=True))

    async def get(self, user_id: int) -> UserFromDB | None:
        user = await self._repo.get(user_id)
        if user:
            return UserFromDB.model_validate(user)
        return None