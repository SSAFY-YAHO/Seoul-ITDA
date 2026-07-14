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
        openai_api_key=settings.openai_api_key,
        openai_model=settings.openai_model,
        openai_timeout_sec=settings.openai_timeout_sec,
    )
    return ChatResponse(
        answer=result.answer,
        sources=result.sources,
        used_openai=result.used_openai,
        fallback=result.fallback,
    )
