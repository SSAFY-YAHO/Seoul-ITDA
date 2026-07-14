from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.post import PostCreateRequest, PostListResponse, PostResponse
from app.services.post_service import create_post, get_post_and_increase_views, list_posts


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


@router.get('/{post_id}', response_model=PostResponse)
def get_post_detail_api(post_id: int, db: Session = Depends(get_db)):
    post = get_post_and_increase_views(db, post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found')
    return post
