from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.post import (
    PostCreateRequest,
    PostDeleteRequest,
    PostDeleteResponse,
    PostListResponse,
    PostResponse,
    PostUpdateRequest,
)
from app.schemas.comment import CommentCreateRequest, CommentListResponse, CommentResponse
from app.services.comment_service import (
    CommentNotFoundError,
    CommentPostNotFoundError,
    ParentCommentNotFoundError,
    create_comment,
    like_comment,
    list_comments,
)
from app.services.post_service import (
    PasswordMismatchError,
    PasswordRequiredError,
    PostNotFoundError,
    create_post,
    delete_post,
    get_post_and_increase_views,
    like_post,
    list_posts,
    update_post,
)


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


@router.post('/{post_id}/like', response_model=PostResponse)
def like_post_api(post_id: int, db: Session = Depends(get_db)):
    try:
        return like_post(db, post_id)
    except PostNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found') from None


@router.get('/{post_id}/comments', response_model=CommentListResponse)
def list_comments_api(post_id: int, db: Session = Depends(get_db)):
    try:
        comments = list_comments(db, post_id)
        return CommentListResponse(items=comments, total=len(comments))
    except CommentPostNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found') from None


@router.post(
    '/{post_id}/comments',
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_comment_api(
    post_id: int,
    payload: CommentCreateRequest,
    db: Session = Depends(get_db),
):
    try:
        return create_comment(db, post_id, payload)
    except CommentPostNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found') from None
    except ParentCommentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Parent comment not found') from None


@router.post('/{post_id}/comments/{comment_id}/like', response_model=CommentResponse)
def like_comment_api(post_id: int, comment_id: int, db: Session = Depends(get_db)):
    try:
        return like_comment(db, post_id, comment_id)
    except CommentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Comment not found') from None


@router.put('/{post_id}', response_model=PostResponse)
def update_post_api(post_id: int, payload: PostUpdateRequest, db: Session = Depends(get_db)):
    try:
        return update_post(db, post_id, payload)
    except PostNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found') from None
    except PasswordRequiredError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Edit password is required') from None
    except PasswordMismatchError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Edit password mismatch') from None


@router.delete('/{post_id}', response_model=PostDeleteResponse)
def delete_post_api(post_id: int, payload: PostDeleteRequest, db: Session = Depends(get_db)):
    try:
        delete_post(db, post_id, payload.edit_password)
        return PostDeleteResponse(message='Post deleted')
    except PostNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found') from None
    except PasswordRequiredError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Edit password is required') from None
    except PasswordMismatchError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Edit password mismatch') from None
