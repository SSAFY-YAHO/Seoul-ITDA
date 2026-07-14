from __future__ import annotations

from pydantic import BaseModel


class DataLoadRequest(BaseModel):
    file_path: str | None = None


class DataLoadResponse(BaseModel):
    message: str
    loaded: int
    updated: int
    skipped: int
    file_path: str
