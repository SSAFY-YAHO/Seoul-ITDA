from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / '.env')


@dataclass(frozen=True)
class Settings:
    root_dir: str = str(ROOT_DIR)
    app_name: str = 'LocalHub Seoul API'
    app_env: str = os.getenv('APP_ENV', 'development')
    app_host: str = os.getenv('APP_HOST', '0.0.0.0')
    app_port: int = int(os.getenv('APP_PORT', '8000'))
    database_url: str = os.getenv('DATABASE_URL', 'sqlite:///./backend/localhub.db')
    seoul_data_path: str = os.getenv('SEOUL_DATA_PATH', 'data')
    chat_ai_provider: str = os.getenv('CHAT_AI_PROVIDER', 'auto')
    local_ai_base_url: str = os.getenv('LOCAL_AI_BASE_URL', 'http://localhost:11434')
    local_ai_model: str = os.getenv('LOCAL_AI_MODEL', 'llama3.1:8b')
    local_ai_timeout_sec: int = int(os.getenv('LOCAL_AI_TIMEOUT_SEC', '30'))
    openai_api_key: str = os.getenv('OPENAI_API_KEY', '')
    openai_model: str = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    openai_timeout_sec: int = int(os.getenv('OPENAI_TIMEOUT_SEC', '15'))
    cors_origins: tuple[str, ...] = tuple(
        origin.strip()
        for origin in os.getenv(
            'CORS_ORIGINS',
            'http://localhost:5173,http://127.0.0.1:5173',
        ).split(',')
        if origin.strip()
    )


settings = Settings()