from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from .faceit.router import router as faceit_router
from .profiles.router import router as profiles_router
from .profiles.models import GameRole
from .reviews.router import router as reviews_router 
from .lfg_statuses.router import router as lfg_router
from .database.setup import create_tables, async_session_maker


async def seed_roles():
    """Добавляет базовые роли в БД, если их там еще нет."""
    roles_to_seed = ["AWP", "ENTRY", "SUPPORT", "IGL", "LURKER"]
    async with async_session_maker() as session:
        for role_name in roles_to_seed:
            exists = await session.execute(select(GameRole).where(GameRole.name == role_name))
            if not exists.scalar_one_or_none():
                session.add(GameRole(name=role_name))
        await session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    await seed_roles()
    yield


app = FastAPI(

    title="Teamify API", 
    lifespan=lifespan

    )

origins = [
    "http://localhost:5173",
    "https://teamify.pro"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows specific origins
    allow_credentials=True, # Allows cookies to be included in cross-origin requests
    allow_methods=["*"],    # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],    # Allows all headers to be sent in the request
)


routers = [faceit_router, profiles_router, reviews_router, lfg_router]

for router in routers:
    app.include_router(router)


app.get("/")
async def index():
    pass