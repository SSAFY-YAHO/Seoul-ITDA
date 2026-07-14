from __future__ import annotations

import json
import re
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
    provider: str
    used_openai: bool
    fallback: bool


PARTICLE_SUFFIXES = (
    '에서',
    '으로',
    '에게',
    '까지',
    '부터',
    '처럼',
    '보다',
    '라도',
    '이라도',
    '이면',
    '면',
    '은',
    '는',
    '이',
    '가',
    '을',
    '를',
    '에',
    '의',
    '도',
    '와',
    '과',
    '좀',
)


def _normalize_keyword(token: str) -> str:
    normalized = re.sub(r'[^0-9A-Za-z가-힣]', '', token.strip().lower())
    if not normalized:
        return ''

    for suffix in PARTICLE_SUFFIXES:
        if normalized.endswith(suffix) and len(normalized) - len(suffix) >= 2:
            normalized = normalized[: -len(suffix)]
            break

    return normalized


def _extract_keywords(question: str) -> list[str]:
    raw_parts = re.split(r'[\s,/?.!]+', question)
    keywords: list[str] = []

    for part in raw_parts:
        normalized = _normalize_keyword(part)
        if len(normalized) >= 2 and normalized not in keywords:
            keywords.append(normalized)

    if not keywords:
        normalized_question = _normalize_keyword(question)
        return [normalized_question] if normalized_question else []

    return keywords[:5]


def _score_text_match(keyword: str, *fields: str) -> int:
    score = 0
    for field in fields:
        if not field:
            continue
        lowered = field.lower()
        if keyword == lowered:
            score += 5
        elif keyword in lowered:
            score += 2
    return score


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
                Attraction.address.like(like_query),
                Attraction.category.like(like_query),
                Attraction.district.like(like_query),
                Attraction.tags.like(like_query),
            ]
        )

    candidates = (
        db.query(Attraction)
        .filter(or_(*conditions))
        .limit(30)
        .all()
    )

    def attraction_score(attraction: Attraction) -> tuple[int, str]:
        total = 0
        for keyword in keywords:
            total += _score_text_match(
                keyword,
                attraction.name,
                attraction.address,
                attraction.district,
                attraction.category,
                attraction.tags,
                attraction.description,
            )
        return total, attraction.name

    ranked = sorted(candidates, key=attraction_score, reverse=True)
    return ranked[:limit]


def _find_relevant_posts(db: Session, question: str, limit: int = 3) -> list[Post]:
    keywords = _extract_keywords(question)
    if not keywords:
        return []

    conditions = []
    for keyword in keywords:
        like_query = f'%{keyword}%'
        conditions.extend([Post.title.like(like_query), Post.content.like(like_query)])

    candidates = (
        db.query(Post)
        .filter(or_(*conditions))
        .order_by(Post.created_at.desc())
        .limit(20)
        .all()
    )

    def post_score(post: Post) -> tuple[int, str]:
        total = 0
        for keyword in keywords:
            total += _score_text_match(keyword, post.title, post.content)
        return total, post.title

    ranked = sorted(candidates, key=post_score, reverse=True)
    return ranked[:limit]


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
            '질문과 바로 연결되는 장소를 찾지 못했습니다. '
            '지역명이나 목적을 같이 적어주면 더 정확해집니다. 예: 성수동 카페, 비 오는 날 실내 데이트, 이번 달 축제'
        )

    parts: list[str] = []
    if attractions:
        parts.append('질문과 가까운 서울 장소를 찾았습니다:')
        for attraction in attractions:
            description = attraction.description.split(' / ')[0].strip() if attraction.description else ''
            summary_bits = [attraction.category, attraction.district]
            if description and description != attraction.address:
                summary_bits.append(description)
            parts.append(
                f"- {attraction.name} | {' · '.join(bit for bit in summary_bits if bit)} | {attraction.address}"
            )
    if posts:
        parts.append('함께 참고할 커뮤니티 글도 있습니다:')
        for post in posts:
            parts.append(f"- {post.title}")
    parts.append('원하면 위 후보 중에서 실내 위주, 산책 위주, 축제 위주처럼 다시 좁혀드릴 수 있습니다.')
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


def _local_ai_answer(
    question: str,
    context_lines: list[str],
    base_url: str,
    model: str,
    timeout_sec: int,
) -> str:
    system_prompt = (
        '너는 서울 관광 도우미다. 반드시 제공된 데이터만 근거로 답하고, '
        '없는 사실은 추측하지 말아라. 답변은 간결하게 정리하라.'
    )
    user_prompt = (
        f'질문: {question}\n'
        '아래 근거 데이터만 사용해서 답변해라:\n'
        + '\n'.join(context_lines)
    )

    payload = {
        'model': model,
        'stream': False,
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt},
        ],
        'options': {'temperature': 0.2},
    }

    normalized_base_url = base_url.rstrip('/')
    request = urllib.request.Request(
        f'{normalized_base_url}/api/chat',
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST',
    )

    with urllib.request.urlopen(request, timeout=timeout_sec) as response:
        data = json.loads(response.read().decode('utf-8'))

    message = data.get('message', {}) if isinstance(data, dict) else {}
    content = message.get('content', '').strip() if isinstance(message, dict) else ''
    if not content:
        raise ValueError('Empty local AI content')
    return content


def answer_chat(
    db: Session,
    question: str,
    ai_provider: str,
    local_ai_base_url: str,
    local_ai_model: str,
    local_ai_timeout_sec: int,
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

    provider = (ai_provider or 'auto').strip().lower()

    def fallback_result() -> ChatResult:
        return ChatResult(
            answer=_local_answer(question, attractions, posts),
            sources=sources,
            provider='fallback',
            used_openai=False,
            fallback=True,
        )

    if not context_lines:
        return fallback_result()

    if provider in {'local', 'auto'} and local_ai_model.strip():
        try:
            answer = _local_ai_answer(
                question,
                context_lines,
                local_ai_base_url,
                local_ai_model,
                local_ai_timeout_sec,
            )
            return ChatResult(
                answer=answer,
                sources=sources,
                provider='local',
                used_openai=False,
                fallback=False,
            )
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
            if provider == 'local':
                return fallback_result()

    if not openai_api_key:
        return fallback_result()

    try:
        answer = _openai_answer(question, context_lines, openai_api_key, openai_model, openai_timeout_sec)
        return ChatResult(
            answer=answer,
            sources=sources,
            provider='openai',
            used_openai=True,
            fallback=False,
        )
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
        return fallback_result()
