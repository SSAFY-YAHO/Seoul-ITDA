from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.post import PostCreateRequest, PostListResponse, PostResponse
from app.services.post_service import create_post, list_posts


router = APIRouter(prefix='/api/posts', tags=['posts'])


@router.get('', response_model=PostListResponse)
def list_posts_api(
    db: Session = Depends(get_db),
    q: str | None = None,
):
    posts = list_posts(db, q)
    return PostListResponse(items=posts, total=len(posts))


@router.post('', response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post_api(payload: PostCreateRequest, db: Session = Depends(get_db)):
    return create_post(db, payload)
