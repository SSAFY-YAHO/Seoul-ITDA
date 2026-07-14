from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.location import LocationListResponse
from app.services.data_service import list_attractions


router = APIRouter(prefix='/api/locations', tags=['locations'])


@router.get('', response_model=LocationListResponse)
def list_locations_api(
    db: Session = Depends(get_db),
    q: str | None = None,
    category: str | None = None,
    district: str | None = None,
    limit: int = 12,
):
    items = list_attractions(
        db,
        q=q,
        category=category,
        district=district,
        limit=limit,
    )
    return LocationListResponse(items=items, total=len(items))