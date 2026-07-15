from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal['user', 'assistant']
    content: str = Field(min_length=1, max_length=1000)


class ChatSource(BaseModel):
    type: Literal['attraction', 'post', 'web']
    title: str
    url: str = ''


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    history: list[ChatMessage] = Field(default_factory=list, max_length=10)


class ChatResponse(BaseModel):
    answer: str
    sources: list[ChatSource]
    provider: str
    mode: Literal['conversation', 'database', 'web']
    used_openai: bool
    fallback: bool
