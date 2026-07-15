from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.attraction import Attraction
from app.models.post import Post


@dataclass(frozen=True)
class ChatSource:
    type: str
    title: str
    url: str = ''


@dataclass
class ChatResult:
    answer: str
    sources: list[ChatSource]
    provider: str
    mode: str
    used_openai: bool
    fallback: bool


PARTICLE_SUFFIXES = (
    '에서', '으로', '에게', '까지', '부터', '처럼', '보다', '라도', '이라도',
    '이면', '면', '은', '는', '이', '가', '을', '를', '에', '의', '도',
    '와', '과', '좀',
)

SEARCH_STOPWORDS = {
    '추천', '추천해줘', '추천해주세요', '알려줘', '알려주세요', '찾아줘', '찾아주세요',
    '어디', '어떤', '관련', '정보', '서울', '장소', '갈만한', '가볼만한', '좋은',
}

GENERIC_PLACE_KEYWORDS = {
    '관광지', '문화시설', '축제', '공연', '행사', '여행코스', '레포츠', '숙박',
    '호텔', '쇼핑', '음식점', '식당', '맛집', '카페', '장소', '명소', '공원',
    '데이트', '산책', '나들이', '실내', '야외', '놀거리', '볼거리', '먹거리',
}

PLACE_INTENT_TERMS = (
    '장소', '갈 곳', '갈곳', '가볼', '어디', '추천', '여행', '관광', '명소', '코스',
    '카페', '맛집', '식당', '음식점', '먹거리', '데이트', '산책', '공원', '전시',
    '박물관', '미술관', '축제', '행사', '숙소', '호텔', '쇼핑', '놀거리', '볼거리',
    '실내', '야외', '나들이', '핫플', '지역',
)

PLACE_FOLLOWUP_TERMS = (
    '그중', '거기', '그곳', '첫 번째', '두 번째', '세 번째', '다른 곳', '조용한 곳',
    '가까운 곳', '더 알려', '조금 더', '그 후보',
)

AI_EXCEPTIONS = (
    urllib.error.HTTPError,
    urllib.error.URLError,
    TimeoutError,
    ValueError,
    json.JSONDecodeError,
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
        if (
            len(normalized) >= 2
            and normalized not in SEARCH_STOPWORDS
            and normalized not in keywords
        ):
            keywords.append(normalized)

    if not keywords:
        normalized_question = _normalize_keyword(question)
        if normalized_question and normalized_question not in SEARCH_STOPWORDS:
            return [normalized_question]
        return []

    return keywords[:8]


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


def _has_specific_match(keywords: list[str], *fields: str) -> bool:
    specific_keywords = [keyword for keyword in keywords if keyword not in GENERIC_PLACE_KEYWORDS]
    if not specific_keywords:
        return True
    matched_count = sum(_score_text_match(keyword, *fields) > 0 for keyword in specific_keywords)
    required_count = 1 if len(specific_keywords) == 1 else 2
    return matched_count >= required_count


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

    candidates = db.query(Attraction).filter(or_(*conditions)).limit(50).all()

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

    candidates = [
        attraction
        for attraction in candidates
        if _has_specific_match(
            keywords,
            attraction.name,
            attraction.address,
            attraction.district,
            attraction.category,
            attraction.tags,
            attraction.description,
        )
    ]
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
        .limit(30)
        .all()
    )

    def post_score(post: Post) -> tuple[int, str]:
        total = sum(_score_text_match(keyword, post.title, post.content) for keyword in keywords)
        return total, post.title

    candidates = [
        post
        for post in candidates
        if _has_specific_match(keywords, post.title, post.content)
    ]
    ranked = sorted(candidates, key=post_score, reverse=True)
    return ranked[:limit]


def _build_context_lines(attractions: list[Attraction], posts: list[Post]) -> list[str]:
    lines: list[str] = []
    for attraction in attractions:
        lines.append(
            '[서울 장소 데이터] '
            f'이름:{attraction.name} / 분류:{attraction.category} / 지역:{attraction.district} / '
            f'주소:{attraction.address} / 설명:{attraction.description}'
        )
    for post in posts:
        lines.append(f'[커뮤니티 데이터] 제목:{post.title} / 내용:{post.content}')
    return lines


def _build_database_sources(
    attractions: list[Attraction],
    posts: list[Post],
) -> list[ChatSource]:
    sources = [
        ChatSource(
            type='attraction',
            title=attraction.name,
            url='https://map.naver.com/p/search/' + urllib.parse.quote(
                ' '.join(part for part in [attraction.name, attraction.address] if part)
            ),
        )
        for attraction in attractions
    ]
    sources.extend(
        ChatSource(type='post', title=post.title, url=f'/posts/{post.id}')
        for post in posts
    )
    return sources


def _local_place_answer(attractions: list[Attraction], posts: list[Post]) -> str:
    parts: list[str] = []
    if attractions:
        parts.append('서울잇다 데이터에서 질문과 가까운 장소를 찾았어요.')
        for attraction in attractions:
            summary_bits = [attraction.category, attraction.district, attraction.address]
            parts.append(f"- {attraction.name} | {' · '.join(bit for bit in summary_bits if bit)}")
    if posts:
        parts.append('함께 참고할 커뮤니티 이야기도 있어요.')
        parts.extend(f'- {post.title}' for post in posts)
    parts.append('원하면 분위기나 이동 지역을 기준으로 더 좁혀드릴게요.')
    return '\n'.join(parts)


def _conversation_fallback() -> str:
    return (
        '지금은 AI 대화 연결을 사용할 수 없어요. 잠시 후 다시 시도해주세요. '
        '서울 장소 질문이라면 지역명이나 목적을 함께 적어주시면 내부 데이터를 먼저 찾아볼게요.'
    )


def _web_search_fallback() -> str:
    return (
        '서울잇다 내부 데이터에서는 관련 장소를 찾지 못했고, 현재 웹 검색 연결도 사용할 수 없어요. '
        '지역명이나 원하는 분위기를 조금 더 구체적으로 알려주시면 다시 찾아볼게요.'
    )


def _sanitize_history(history: list[dict[str, str]] | None, limit: int = 10) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = []
    for item in (history or [])[-limit:]:
        role = str(item.get('role', '')).strip().lower()
        content = str(item.get('content', '')).strip()
        if role in {'user', 'assistant'} and content:
            messages.append({'role': role, 'content': content[:1000]})
    return messages


def _last_user_message(history: list[dict[str, str]]) -> str:
    for message in reversed(history):
        if message['role'] == 'user':
            return message['content']
    return ''


def _is_place_search(question: str, history: list[dict[str, str]] | None = None) -> bool:
    lowered = question.strip().lower()
    if any(term in lowered for term in PLACE_INTENT_TERMS):
        return True

    if any(term in lowered for term in PLACE_FOLLOWUP_TERMS):
        previous_user_message = _last_user_message(_sanitize_history(history))
        return any(term in previous_user_message.lower() for term in PLACE_INTENT_TERMS)

    return False


def _build_place_search_question(question: str, history: list[dict[str, str]]) -> str:
    if any(term in question.lower() for term in PLACE_FOLLOWUP_TERMS):
        previous_user_message = _last_user_message(history)
        if previous_user_message:
            return f'{previous_user_message} {question}'
    return question


def _post_json(url: str, payload: dict[str, Any], api_key: str, timeout_sec: int) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
        },
        method='POST',
    )
    with urllib.request.urlopen(request, timeout=timeout_sec) as response:
        return json.loads(response.read().decode('utf-8'))


def _openai_chat_answer(
    question: str,
    history: list[dict[str, str]],
    context_lines: list[str],
    api_key: str,
    model: str,
    timeout_sec: int,
) -> str:
    if context_lines:
        system_prompt = (
            '너는 서울잇다의 다정한 AI 안내자다. 제공된 내부 서울 데이터만 근거로 장소를 안내하고, '
            '데이터에 없는 세부 사실은 만들지 마라. 답변은 자연스러운 한국어로 간결하게 작성하라.\n\n'
            '내부 데이터:\n' + '\n'.join(context_lines)
        )
    else:
        system_prompt = (
            '너는 서울잇다의 다정한 대화형 AI다. 사용자의 말에 자연스러운 한국어로 답하고 '
            '이전 대화의 맥락을 이어가라. 일반 대화에서는 억지로 서울 장소를 추천하지 마라.'
        )

    payload = {
        'model': model,
        'messages': [
            {'role': 'system', 'content': system_prompt},
            *history,
            {'role': 'user', 'content': question},
        ],
    }
    data = _post_json(
        'https://api.openai.com/v1/chat/completions',
        payload,
        api_key,
        timeout_sec,
    )
    choices = data.get('choices', [])
    if not choices:
        raise ValueError('Empty OpenAI choices')
    content = choices[0].get('message', {}).get('content', '').strip()
    if not content:
        raise ValueError('Empty OpenAI content')
    return content


def _local_ai_answer(
    question: str,
    history: list[dict[str, str]],
    context_lines: list[str],
    base_url: str,
    model: str,
    timeout_sec: int,
) -> str:
    if context_lines:
        system_prompt = (
            '너는 서울잇다의 다정한 AI 안내자다. 아래 내부 데이터만 근거로 장소를 안내하고 '
            '없는 사실은 추측하지 마라.\n\n내부 데이터:\n' + '\n'.join(context_lines)
        )
    else:
        system_prompt = (
            '너는 서울잇다의 다정한 대화형 AI다. 자연스러운 한국어로 대화하고 '
            '일반 대화에서는 억지로 서울 장소를 추천하지 마라.'
        )

    payload = {
        'model': model,
        'stream': False,
        'messages': [
            {'role': 'system', 'content': system_prompt},
            *history,
            {'role': 'user', 'content': question},
        ],
        'options': {'temperature': 0.5 if not context_lines else 0.2},
    }
    normalized_base_url = base_url.rstrip('/')
    request = urllib.request.Request(
        f'{normalized_base_url}/api/chat',
        data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
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


def _extract_web_response(data: dict[str, Any]) -> tuple[str, list[ChatSource]]:
    text_parts: list[str] = []
    sources: list[ChatSource] = []
    seen_urls: set[str] = set()

    for output_item in data.get('output', []):
        if not isinstance(output_item, dict) or output_item.get('type') != 'message':
            continue
        for content_item in output_item.get('content', []):
            if not isinstance(content_item, dict) or content_item.get('type') != 'output_text':
                continue
            text = str(content_item.get('text', '')).strip()
            if text:
                text_parts.append(text)
            for annotation in content_item.get('annotations', []):
                if not isinstance(annotation, dict) or annotation.get('type') != 'url_citation':
                    continue
                url = str(annotation.get('url', '')).strip()
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)
                sources.append(
                    ChatSource(
                        type='web',
                        title=str(annotation.get('title', '')).strip() or url,
                        url=url,
                    )
                )

    answer = '\n'.join(text_parts).strip()
    if not answer:
        raise ValueError('Empty OpenAI web search content')
    return answer, sources[:6]


def _openai_web_search(
    question: str,
    history: list[dict[str, str]],
    api_key: str,
    model: str,
    timeout_sec: int,
) -> tuple[str, list[ChatSource]]:
    payload = {
        'model': model,
        'instructions': (
            '너는 서울잇다의 장소 탐색 도우미다. 서울잇다 내부 DB에 결과가 없어 웹 검색이 요청되었다. '
            '서울 안의 실제 장소를 찾아 자연스러운 한국어로 답하고, 최신 정보는 공식 기관이나 장소 공식 페이지를 '
            '우선 확인하라. 확인되지 않은 운영시간이나 가격을 단정하지 마라.'
        ),
        'input': [*history, {'role': 'user', 'content': question}],
        'tools': [{'type': 'web_search', 'search_context_size': 'low'}],
        'tool_choice': 'auto',
    }
    data = _post_json(
        'https://api.openai.com/v1/responses',
        payload,
        api_key,
        timeout_sec,
    )
    return _extract_web_response(data)


def _configured_ai_answer(
    *,
    provider: str,
    question: str,
    history: list[dict[str, str]],
    context_lines: list[str],
    local_ai_base_url: str,
    local_ai_model: str,
    local_ai_timeout_sec: int,
    openai_api_key: str,
    openai_model: str,
    openai_timeout_sec: int,
) -> tuple[str, str, bool] | None:
    if provider in {'local', 'auto'} and local_ai_model.strip():
        try:
            answer = _local_ai_answer(
                question,
                history,
                context_lines,
                local_ai_base_url,
                local_ai_model,
                local_ai_timeout_sec,
            )
            return answer, 'local', False
        except AI_EXCEPTIONS:
            if provider == 'local':
                return None

    if provider in {'openai', 'auto'} and openai_api_key:
        try:
            answer = _openai_chat_answer(
                question,
                history,
                context_lines,
                openai_api_key,
                openai_model,
                openai_timeout_sec,
            )
            return answer, 'openai', True
        except AI_EXCEPTIONS:
            return None

    return None


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
    history: list[dict[str, str]] | None = None,
    web_search_enabled: bool = True,
    openai_web_search_model: str = 'gpt-5.4-mini',
    openai_web_search_timeout_sec: int = 30,
) -> ChatResult:
    clean_history = _sanitize_history(history)
    provider = (ai_provider or 'openai').strip().lower()

    if not _is_place_search(question, clean_history):
        ai_result = _configured_ai_answer(
            provider=provider,
            question=question,
            history=clean_history,
            context_lines=[],
            local_ai_base_url=local_ai_base_url,
            local_ai_model=local_ai_model,
            local_ai_timeout_sec=local_ai_timeout_sec,
            openai_api_key=openai_api_key,
            openai_model=openai_model,
            openai_timeout_sec=openai_timeout_sec,
        )
        if ai_result:
            answer, used_provider, used_openai = ai_result
            return ChatResult(answer, [], used_provider, 'conversation', used_openai, False)
        return ChatResult(_conversation_fallback(), [], 'fallback', 'conversation', False, True)

    search_question = _build_place_search_question(question, clean_history)
    attractions = _find_relevant_attractions(db, search_question)
    posts = _find_relevant_posts(db, search_question)
    context_lines = _build_context_lines(attractions, posts)

    if context_lines:
        sources = _build_database_sources(attractions, posts)
        ai_result = _configured_ai_answer(
            provider=provider,
            question=question,
            history=clean_history,
            context_lines=context_lines,
            local_ai_base_url=local_ai_base_url,
            local_ai_model=local_ai_model,
            local_ai_timeout_sec=local_ai_timeout_sec,
            openai_api_key=openai_api_key,
            openai_model=openai_model,
            openai_timeout_sec=openai_timeout_sec,
        )
        if ai_result:
            answer, used_provider, used_openai = ai_result
            return ChatResult(answer, sources, used_provider, 'database', used_openai, False)
        return ChatResult(
            _local_place_answer(attractions, posts),
            sources,
            'fallback',
            'database',
            False,
            True,
        )

    if web_search_enabled and openai_api_key and openai_web_search_model.strip():
        try:
            answer, sources = _openai_web_search(
                question,
                clean_history,
                openai_api_key,
                openai_web_search_model,
                openai_web_search_timeout_sec,
            )
            return ChatResult(answer, sources, 'openai', 'web', True, False)
        except AI_EXCEPTIONS:
            pass

    return ChatResult(_web_search_fallback(), [], 'fallback', 'web', False, True)
