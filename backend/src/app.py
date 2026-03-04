import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from .auth.router import router as auth_router
from .faceit.router import router as faceit_router
from .profiles.router import router as profiles_router
from .profiles.models import GameRole
from .reviews.router import router as reviews_router
from .lfg_statuses.router import router as lfg_router
from .database.setup import create_tables, async_session_maker


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def seed_roles():
    roles_to_seed = ["AWP", "ENTRY/ANCHOR", "SUPPORT", "IGL", "LURKER"]
    async with async_session_maker() as session:
        for role_name in roles_to_seed:
            exists = await session.execute(
                select(GameRole).where(GameRole.name == role_name)
            )
            if not exists.scalar_one_or_none():
                session.add(GameRole(name=role_name))
        await session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    await seed_roles()
    logger.info("Application started.")
    yield
    logger.info("Application shutting down.")


app = FastAPI(title="Teamify API", lifespan=lifespan)

origins = [
    "http://localhost:5173",
    "https://teamify.pro",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

routers = [auth_router, faceit_router, profiles_router, reviews_router, lfg_router]
for router in routers:
    app.include_router(router)


@app.get("/")
async def index():
    return {"status": "ok"}
