from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class PostCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    edit_password: str = Field(min_length=1, max_length=100)


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    views: int
    likes: int
    created_at: datetime
    updated_at: datetime

    model_config = {'from_attributes': True}


class PostListResponse(BaseModel):
    items: list[PostResponse]
    total: int


class PostUpdateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    edit_password: str | None = None


class PostDeleteRequest(BaseModel):
    edit_password: str | None = None


class PostDeleteResponse(BaseModel):
    message: str
