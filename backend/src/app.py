from contextlib import asynccontextmanager

from fastapi import FastAPI

from .users.router import router as users_router
from .database.setup import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield


app = FastAPI(

    title="Teamify API", 
    lifespan=lifespan

    )

routers = [users_router]

for router in routers:
    app.include_router(router)


app.get("/")
async def index():
    pass