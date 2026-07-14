from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class LocationResponse(BaseModel):
    id: int
    name: str
    category: str
    district: str
    description: str
    address: str
    tags: str
    created_at: datetime
    updated_at: datetime

    model_config = {'from_attributes': True}


class LocationListResponse(BaseModel):
    items: list[LocationResponse]
    total: int