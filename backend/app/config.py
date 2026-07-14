from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / '.env')


@dataclass(frozen=True)
class Settings:
    app_name: str = 'LocalHub Seoul API'
    app_env: str = os.getenv('APP_ENV', 'development')
    app_host: str = os.getenv('APP_HOST', '0.0.0.0')
    app_port: int = int(os.getenv('APP_PORT', '8000'))
    database_url: str = os.getenv('DATABASE_URL', 'sqlite:///./backend/localhub.db')
    cors_origins: tuple[str, ...] = tuple(
        origin.strip()
        for origin in os.getenv(
            'CORS_ORIGINS',
            'http://localhost:5173,http://127.0.0.1:5173',
        ).split(',')
        if origin.strip()
    )


settings = Settings()