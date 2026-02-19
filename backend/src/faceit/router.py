from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from .config import faceit_config


router = APIRouter("/faceit")


@router.get("/oauth2/login")
async def login_with_faceit():
    auth_url = f"{faceit_config.FACEIT_AUTH_ENDPOINT}?response_type=code&client_id={faceit_config.FACEIT_CLIENT_ID}&redirect_popup=true"
    return RedirectResponse(url=auth_url)


@router.post("/oauth2/callback")
async def faceit_auth_callback(
    code: str,
    
    
    
    ):
   pass
