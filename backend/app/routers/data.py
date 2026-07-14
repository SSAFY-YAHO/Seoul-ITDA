from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.schemas.data import DataLoadRequest, DataLoadResponse
from app.services.data_service import load_attractions_from_file


router = APIRouter(prefix='/api/data', tags=['data'])


@router.post('/load', response_model=DataLoadResponse)
def load_data_api(payload: DataLoadRequest, db: Session = Depends(get_db)):
    target_path = payload.file_path or settings.seoul_data_path
    absolute_path = Path(settings.root_dir) / target_path

    try:
        result = load_attractions_from_file(db, str(absolute_path))
        return DataLoadResponse(**result)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Data load failed') from exc
