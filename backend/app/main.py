from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.models import Attraction, Comment, Post
from app.routers.chat import router as chat_router
from app.routers.data import router as data_router
from app.routers.festivals import router as festivals_router
from app.routers.health import router as health_router
from app.routers.locations import router as locations_router
from app.routers.posts import router as posts_router
from app.services.data_service import contains_mojibake, load_attractions_from_file
from sqlalchemy import inspect, text
# asjf;oiaje;ajflasdjf;lasjfl;

def ensure_attraction_detail_columns() -> None:
    """기존 SQLite DB에도 상세 정보 컬럼을 비파괴 방식으로 추가한다."""
    columns = {column['name'] for column in inspect(engine).get_columns('attractions')}
    with engine.begin() as connection:
        if 'image_url' not in columns:
            connection.execute(text("ALTER TABLE attractions ADD COLUMN image_url VARCHAR(1000) NOT NULL DEFAULT ''"))
        if 'thumbnail_url' not in columns:
            connection.execute(text("ALTER TABLE attractions ADD COLUMN thumbnail_url VARCHAR(1000) NOT NULL DEFAULT ''"))
        if 'telephone' not in columns:
            connection.execute(text("ALTER TABLE attractions ADD COLUMN telephone VARCHAR(200) NOT NULL DEFAULT ''"))
        if 'longitude' not in columns:
            connection.execute(text("ALTER TABLE attractions ADD COLUMN longitude FLOAT"))
        if 'latitude' not in columns:
            connection.execute(text("ALTER TABLE attractions ADD COLUMN latitude FLOAT"))


def ensure_post_like_column() -> None:
    """기존 SQLite 게시글 테이블에 좋아요 수 컬럼을 안전하게 추가합니다."""
    columns = {column['name'] for column in inspect(engine).get_columns('posts')}
    if 'likes' not in columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE posts ADD COLUMN likes INTEGER NOT NULL DEFAULT 0"))


def ensure_post_image_column() -> None:
    """기존 SQLite 게시글 테이블에 첨부 이미지 URL 컬럼을 추가합니다."""
    columns = {column['name'] for column in inspect(engine).get_columns('posts')}
    if 'images_json' not in columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE posts ADD COLUMN images_json TEXT NOT NULL DEFAULT '[]'"))


def ensure_comment_parent_column() -> None:
    """기존 SQLite 댓글 테이블에 대댓글 부모 컬럼을 추가한다."""
    inspector = inspect(engine)
    if 'comments' not in inspector.get_table_names():
        return
    columns = {column['name'] for column in inspector.get_columns('comments')}
    if 'parent_id' not in columns:
        with engine.begin() as connection:
            connection.execute(text('ALTER TABLE comments ADD COLUMN parent_id INTEGER'))


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    ensure_attraction_detail_columns()
    ensure_post_like_column()
    ensure_post_image_column()
    ensure_comment_parent_column()

    session = SessionLocal()
    try:
        has_attractions = session.query(Attraction.id).first() is not None
        needs_image_sync = session.query(Attraction.id).filter(Attraction.image_url != '').first() is None
        needs_contact_sync = session.query(Attraction.id).filter(Attraction.telephone != '').first() is None
        needs_coordinate_sync = session.query(Attraction.id).filter(Attraction.longitude.is_not(None)).first() is None
        encoding_samples = session.query(Attraction.name).limit(20).all()
        needs_encoding_sync = any(contains_mojibake(name) for (name,) in encoding_samples)
        if (
            not has_attractions
            or needs_image_sync
            or needs_contact_sync
            or needs_coordinate_sync
            or needs_encoding_sync
        ):
            default_data_path = Path(settings.root_dir) / settings.seoul_data_path
            try:
                load_attractions_from_file(session, str(default_data_path))
            except FileNotFoundError:
                session.rollback()

        has_posts = session.query(Post.id).first() is not None
        if not has_posts:
            sample_posts = [
                Post(   
                    title='서울 도심 반나절 코스 추천',
                    content='종로와 을지로를 중심으로 걸어서 즐길 수 있는 코스를 공유합니다.',
                    edit_password='demo1234',
                ),
                Post(
                    title='비 오는 날 실내 문화시설 후기',
                    content='비 오는 날에도 이동하기 쉬운 실내 전시관 위주로 정리해봤어요.',
                    edit_password='demo1234',
                ),
            ]
            session.add_all(sample_posts)
            session.commit()
    finally:
        session.close()

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
app.include_router(festivals_router)
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
