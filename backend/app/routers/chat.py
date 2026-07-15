from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import answer_chat


router = APIRouter(prefix='/api', tags=['chat'])


@router.post('/chat', response_model=ChatResponse)
def chat_api(payload: ChatRequest, db: Session = Depends(get_db)):
    result = answer_chat(
        db=db,
        question=payload.question,
        history=[message.model_dump() for message in payload.history],
        ai_provider=settings.chat_ai_provider,
        local_ai_base_url=settings.local_ai_base_url,
        local_ai_model=settings.local_ai_model,
        local_ai_timeout_sec=settings.local_ai_timeout_sec,
        openai_api_key=settings.openai_api_key,
        openai_model=settings.openai_model,
        openai_web_search_model=settings.openai_web_search_model,
        openai_timeout_sec=settings.openai_timeout_sec,
        openai_web_search_timeout_sec=settings.openai_web_search_timeout_sec,
        web_search_enabled=settings.chat_web_search_enabled,
    )
    return ChatResponse(
        answer=result.answer,
        sources=[
            {'type': source.type, 'title': source.title, 'url': source.url}
            for source in result.sources
        ],
        provider=result.provider,
        mode=result.mode,
        used_openai=result.used_openai,
        fallback=result.fallback,
    )
