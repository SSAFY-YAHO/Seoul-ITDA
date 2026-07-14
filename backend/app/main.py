from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.models import Attraction, Post
from app.routers.chat import router as chat_router
from app.routers.data import router as data_router
from app.routers.health import router as health_router
from app.routers.locations import router as locations_router
from app.routers.posts import router as posts_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(health_router)
app.include_router(locations_router)
app.include_router(posts_router)
app.include_router(data_router)
app.include_router(chat_router)


@app.get('/')
def read_root():
    return {
        'service': settings.app_name,
        'environment': settings.app_env,
        'docs': '/docs',
    }