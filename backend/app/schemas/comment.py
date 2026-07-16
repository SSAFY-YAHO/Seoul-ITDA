from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class CommentCreateRequest(BaseModel):
    author: str = Field(min_length=1, max_length=30)
    content: str = Field(min_length=1, max_length=1000)

    @field_validator('author', 'content')
    @classmethod
    def reject_whitespace_only(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError('must not be blank')
        return value


class CommentResponse(BaseModel):
    id: int
    post_id: int
    author: str
    content: str
    likes: int
    created_at: datetime

    model_config = {'from_attributes': True}


class CommentListResponse(BaseModel):
    items: list[CommentResponse]
    total: int

