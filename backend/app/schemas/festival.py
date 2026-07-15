from __future__ import annotations

from pydantic import BaseModel


class FestivalResponse(BaseModel):
    id: str
    title: str
    category: str
    region: str
    place: str
    address: str
    description: str
    imageUrl: str
    homepageUrl: str
    phone: str
    longitude: float | None = None
    latitude: float | None = None
    startDate: str | None = None
    endDate: str | None = None


class FestivalListResponse(BaseModel):
    items: list[FestivalResponse]
    total: int
