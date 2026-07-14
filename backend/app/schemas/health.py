from __future__ import annotations

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    environment: str
    database_url: str
    allowed_origins: list[str]