from __future__ import annotations

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.post import Post
from app.schemas.post import PostCreateRequest, PostUpdateRequest


class PostNotFoundError(Exception):
    pass


class PasswordRequiredError(Exception):
    pass


class PasswordMismatchError(Exception):
    pass


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


def get_post_or_none(db: Session, post_id: int) -> Post | None:
    return db.query(Post).filter(Post.id == post_id).first()


def get_post_and_increase_views(db: Session, post_id: int) -> Post | None:
    post = get_post_or_none(db, post_id)
    if post is None:
        return None
    post.views += 1
    db.commit()
    db.refresh(post)
    return post


def update_post(db: Session, post_id: int, payload: PostUpdateRequest) -> Post:
    post = get_post_or_none(db, post_id)
    if post is None:
        raise PostNotFoundError()
    if payload.edit_password is None or payload.edit_password.strip() == '':
        raise PasswordRequiredError()
    if payload.edit_password != post.edit_password:
        raise PasswordMismatchError()

    post.title = payload.title
    post.content = payload.content
    db.commit()
    db.refresh(post)
    return post
