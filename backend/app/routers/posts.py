from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.post import PostCreateRequest, PostResponse
from app.services.post_service import create_post


router = APIRouter(prefix='/api/posts', tags=['posts'])


@router.post('', response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post_api(payload: PostCreateRequest, db: Session = Depends(get_db)):
    return create_post(db, payload)
