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
    created_at: datetime
    updated_at: datetime

    model_config = {'from_attributes': True}
