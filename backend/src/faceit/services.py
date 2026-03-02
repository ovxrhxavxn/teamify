from .repositories import AbstractFaceitRepository
from .schemas import (
    FaceitTokenResponse, 
    FaceitUserInfoResponse, 
    FaceitDataFromDB, 
    FaceitAuthData,
    FaceitPlayerStatsResponse,
    FaceitData,
    FaceitPlayerDetailsResponse
)


class FaceitService:

    def __init__(self, repo: type[AbstractFaceitRepository]):
        self._repo = repo()


    async def get_token(self, code: str, code_verifier: str):
        data = await self._repo.get_token(code, code_verifier)
        return FaceitTokenResponse.model_validate(data)


    async def get_user_info(self, accsess_token: str):
        data = await self._repo.get_user_info(accsess_token)

        return FaceitUserInfoResponse.model_validate(data)
    
    async def get_player_stats(self, player_id: str):
        data = await self._repo.get_player_stats(player_id)
        if not data:
            return None
        lifetime_stats = data.get("lifetime", {})
        return FaceitPlayerStatsResponse.model_validate(lifetime_stats)


    async def get_faceit_data_by_guid(self, guid: str):
        faceit_data = await self._repo.get_faceit_data_by_guid(guid)

        if faceit_data:
            return FaceitDataFromDB.model_validate(faceit_data)
        
        return faceit_data
    

    async def add_faceit_auth_data(self, schema: FaceitAuthData):
        faceit_auth_data_id = await self._repo.add_faceit_auth_data(schema.model_dump())
        return faceit_auth_data_id


    async def add_faceit_data(self, schema: FaceitData):
        faceit_data_id = await self._repo.add_faceit_data(schema.model_dump())
        return faceit_data_id
    

    async def get_player_details(self, player_id: str):
        data = await self._repo.get_player_details(player_id)
        if not data:
            return None
        return FaceitPlayerDetailsResponse.model_validate(data)
    

    async def get_faceit_data_by_user_id(self, user_id: int):
        faceit_data = await self._repo.get_faceit_data_by_user_id(user_id)
        if faceit_data:
            return FaceitDataFromDB.model_validate(faceit_data)
        return None