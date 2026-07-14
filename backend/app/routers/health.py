from __future__ import annotations

from fastapi import APIRouter

from app.config import settings
from app.schemas.health import HealthResponse


router = APIRouter(prefix='/api', tags=['health'])


@router.get('/health', response_model=HealthResponse)
def read_health():
    return HealthResponse(
        status='ok',
        environment=settings.app_env,
        database_url=settings.database_url,
        allowed_origins=list(settings.cors_origins),
    )