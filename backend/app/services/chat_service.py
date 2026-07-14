from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.attraction import Attraction
from app.models.post import Post


@dataclass
class ChatResult:
    answer: str
    sources: list[str]
    used_openai: bool
    fallback: bool


def _extract_keywords(question: str) -> list[str]:
    raw_parts = [part.strip() for part in question.replace(',', ' ').replace('/', ' ').split()]
    keywords = [part for part in raw_parts if len(part) >= 2]
    if not keywords:
        return [question.strip()] if question.strip() else []
    return keywords[:5]


def _find_relevant_attractions(db: Session, question: str, limit: int = 3) -> list[Attraction]:
    keywords = _extract_keywords(question)
    if not keywords:
        return []

    conditions = []
    for keyword in keywords:
        like_query = f'%{keyword}%'
        conditions.extend(
            [
                Attraction.name.like(like_query),
                Attraction.description.like(like_query),
                Attraction.category.like(like_query),
                Attraction.district.like(like_query),
                Attraction.tags.like(like_query),
            ]
        )

    return (
        db.query(Attraction)
        .filter(or_(*conditions))
        .limit(limit)
        .all()
    )


def _find_relevant_posts(db: Session, question: str, limit: int = 3) -> list[Post]:
    keywords = _extract_keywords(question)
    if not keywords:
        return []

    conditions = []
    for keyword in keywords:
        like_query = f'%{keyword}%'
        conditions.extend([Post.title.like(like_query), Post.content.like(like_query)])

    return (
        db.query(Post)
        .filter(or_(*conditions))
        .order_by(Post.created_at.desc())
        .limit(limit)
        .all()
    )


def _build_context_lines(attractions: list[Attraction], posts: list[Post]) -> list[str]:
    lines: list[str] = []
    for attraction in attractions:
        lines.append(
            f"[관광데이터] 이름:{attraction.name} / 분류:{attraction.category} / 지역:{attraction.district} / 설명:{attraction.description}"
        )
    for post in posts:
        lines.append(f"[커뮤니티] 제목:{post.title} / 내용:{post.content}")
    return lines


def _local_answer(question: str, attractions: list[Attraction], posts: list[Post]) -> str:
    if not attractions and not posts:
        return (
            '질문과 직접 매칭되는 서울 관광 데이터나 커뮤니티 글을 찾지 못했습니다. '
            '질문 키워드를 더 구체적으로 입력해 주세요.'
        )

    parts: list[str] = []
    if attractions:
        parts.append('관광 데이터 기준 추천:')
        for attraction in attractions:
            parts.append(f"- {attraction.name} ({attraction.category}, {attraction.district})")
    if posts:
        parts.append('커뮤니티 참고 글:')
        for post in posts:
            parts.append(f"- {post.title}")
    parts.append('위 내용은 현재 저장된 서울 데이터와 커뮤니티 DB를 기반으로 정리했습니다.')
    return '\n'.join(parts)


def _openai_answer(
    question: str,
    context_lines: list[str],
    api_key: str,
    model: str,
    timeout_sec: int,
) -> str:
    system_prompt = (
        '너는 서울 관광 도우미다. 반드시 제공된 데이터만 근거로 답해라. '
        '데이터에 없는 사실은 모른다고 답해라.'
    )
    user_prompt = (
        f"질문: {question}\n"
        '아래 근거 데이터만 사용해서 답변해라:\n'
        + '\n'.join(context_lines)
    )

    payload = {
        'model': model,
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt},
        ],
        'temperature': 0.2,
    }

    request = urllib.request.Request(
        'https://api.openai.com/v1/chat/completions',
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
        },
        method='POST',
    )

    with urllib.request.urlopen(request, timeout=timeout_sec) as response:
        data = json.loads(response.read().decode('utf-8'))

    choices = data.get('choices', [])
    if not choices:
        raise ValueError('Empty OpenAI choices')
    content = choices[0].get('message', {}).get('content', '').strip()
    if not content:
        raise ValueError('Empty OpenAI content')
    return content


def answer_chat(
    db: Session,
    question: str,
    openai_api_key: str,
    openai_model: str,
    openai_timeout_sec: int,
) -> ChatResult:
    attractions = _find_relevant_attractions(db, question)
    posts = _find_relevant_posts(db, question)
    context_lines = _build_context_lines(attractions, posts)

    sources = [
        f"attraction:{attraction.name}" for attraction in attractions
    ] + [
        f"post:{post.id}" for post in posts
    ]

    if not openai_api_key:
        return ChatResult(
            answer=_local_answer(question, attractions, posts),
            sources=sources,
            used_openai=False,
            fallback=True,
        )

    if not context_lines:
        return ChatResult(
            answer=_local_answer(question, attractions, posts),
            sources=sources,
            used_openai=False,
            fallback=True,
        )

    try:
        answer = _openai_answer(question, context_lines, openai_api_key, openai_model, openai_timeout_sec)
        return ChatResult(answer=answer, sources=sources, used_openai=True, fallback=False)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
        return ChatResult(
            answer=_local_answer(question, attractions, posts),
            sources=sources,
            used_openai=False,
            fallback=True,
        )
