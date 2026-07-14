from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.schemas.festival import FestivalListResponse
from app.services.festival_service import list_festivals
from app.services.data_service import list_attractions


router = APIRouter(prefix='/api/festivals', tags=['festivals'])


@router.get('', response_model=FestivalListResponse)
def list_festivals_api(
    db: Session = Depends(get_db),
    q: str | None = None,
    status: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
):
    fallback_attractions = list_attractions(db, category='축제', limit=50)
    items = list_festivals(
        root_dir=settings.root_dir,
        attractions=fallback_attractions,
        keyword=q,
        status=status,
        start_date=start_date,
        end_date=end_date,
    )
    return FestivalListResponse(items=items, total=len(items))