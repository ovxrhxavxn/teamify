from .repositories import AbstractUserRepository
from .schemas import User, UserFromDB


class UserService:

    def __init__(self, repo: type[AbstractUserRepository[UserFromDB]]):
        self._repo = repo()


    async def add(self, schema: User):
        user_id = await self._repo.add(schema.model_dump())
        return user_id
    

    async def get(self, id: int):
        user = await self._repo.get(id)
        return UserFromDB.model_validate(user)