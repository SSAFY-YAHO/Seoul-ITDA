from __future__ import annotations

from sqlalchemy import or_
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


def list_posts(db: Session, query: str | None = None) -> list[Post]:
    statement = db.query(Post)
    if query:
        like_query = f'%{query}%'
        statement = statement.filter(
            or_(
                Post.title.like(like_query),
                Post.content.like(like_query),
            )
        )
    return statement.order_by(Post.created_at.desc()).all()
