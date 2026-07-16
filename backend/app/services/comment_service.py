from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.models.post import Post
from app.schemas.comment import CommentCreateRequest


class CommentPostNotFoundError(Exception):
    pass


class CommentNotFoundError(Exception):
    pass


class ParentCommentNotFoundError(Exception):
    pass


def ensure_post_exists(db: Session, post_id: int) -> None:
    if db.query(Post.id).filter(Post.id == post_id).first() is None:
        raise CommentPostNotFoundError()


def list_comments(db: Session, post_id: int) -> list[Comment]:
    ensure_post_exists(db, post_id)
    return (
        db.query(Comment)
        .filter(Comment.post_id == post_id)
        .order_by(Comment.created_at.asc(), Comment.id.asc())
        .all()
    )


def create_comment(db: Session, post_id: int, payload: CommentCreateRequest) -> Comment:
    ensure_post_exists(db, post_id)
    if payload.parent_id is not None:
        parent = (
            db.query(Comment)
            .filter(
                Comment.id == payload.parent_id,
                Comment.post_id == post_id,
                Comment.parent_id.is_(None),
            )
            .first()
        )
        if parent is None:
            raise ParentCommentNotFoundError()
    comment = Comment(
        post_id=post_id,
        parent_id=payload.parent_id,
        author=payload.author,
        content=payload.content,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def like_comment(db: Session, post_id: int, comment_id: int) -> Comment:
    comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id, Comment.post_id == post_id)
        .first()
    )
    if comment is None:
        raise CommentNotFoundError()
    comment.likes += 1
    db.commit()
    db.refresh(comment)
    return comment
