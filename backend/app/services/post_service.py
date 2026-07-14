from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.post import Post
from app.schemas.post import PostCreateRequest


def create_post(db: Session, payload: PostCreateRequest) -> Post:
    post = Post(
        title=payload.title,
        content=payload.content,
        edit_password=payload.edit_password,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post
