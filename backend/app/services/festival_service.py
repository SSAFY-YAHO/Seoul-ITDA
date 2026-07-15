from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from app.models.attraction import Attraction


def _extract_district(addr1: str) -> str:
    parts = [part for part in addr1.split() if part]
    if len(parts) >= 2 and parts[0].startswith('서울'):
        return parts[1]
    return '서울'


def _normalize_date_value(raw_value: object) -> str | None:
    if raw_value is None:
        return None

    raw = str(raw_value).strip()
    if not raw:
        return None

    digits = ''.join(ch for ch in raw if ch.isdigit())
    if len(digits) != 8:
        return None

    year = int(digits[0:4])
    month = int(digits[4:6])
    day = int(digits[6:8])
    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return None


def _to_date(raw_value: str | None) -> date | None:
    if not raw_value:
        return None
    try:
        return date.fromisoformat(raw_value)
    except ValueError:
        return None


def _to_float(raw_value: object) -> float | None:
    try:
        return float(str(raw_value).strip())
    except (TypeError, ValueError):
        return None


def _festival_status(start_date: date | None, end_date: date | None, today: date) -> str:
    if not start_date:
        return 'unknown'

    festival_end = end_date or start_date
    if today < start_date:
        return 'upcoming'
    if today > festival_end:
        return 'ended'
    return 'ongoing'


def _normalize_festival_item(item: dict) -> dict[str, str | None]:
    addr1 = str(item.get('addr1', '')).strip()
    addr2 = str(item.get('addr2', '')).strip()
    address = ' '.join(part for part in [addr1, addr2] if part).strip()
    phone = str(item.get('tel', '')).strip()
    place = addr2 or addr1
    region = _extract_district(addr1)
    start_date = _normalize_date_value(
        item.get('eventstartdate') or item.get('startdate') or item.get('startDate')
    )
    end_date = _normalize_date_value(
        item.get('eventenddate') or item.get('enddate') or item.get('endDate')
    )

    description_parts = []
    if place and place != address:
        description_parts.append(f'장소: {place}')
    if phone:
        description_parts.append(f'문의: {phone}')
    if not start_date:
        description_parts.append('현재 저장된 원본 데이터에는 시작일과 종료일 정보가 포함되어 있지 않습니다.')

    return {
        'id': str(item.get('contentid', '')).strip() or str(item.get('title', '')).strip(),
        'title': str(item.get('title', '')).strip() or '축제',
        'category': '축제공연행사',
        'region': region,
        'place': place,
        'address': address,
        'description': ' '.join(part for part in description_parts if part).strip(),
        'imageUrl': str(item.get('firstimage', '')).strip() or str(item.get('firstimage2', '')).strip(),
        'homepageUrl': str(item.get('homepage', '')).strip(),
        'phone': phone,
        'longitude': _to_float(item.get('mapx')),
        'latitude': _to_float(item.get('mapy')),
        'startDate': start_date,
        'endDate': end_date,
    }


def _fallback_from_attractions(attractions: list[Attraction]) -> list[dict[str, str | None]]:
    items: list[dict[str, str | None]] = []
    for attraction in attractions:
        items.append(
            {
                'id': str(attraction.id),
                'title': attraction.name,
                'category': attraction.category,
                'region': attraction.district,
                'place': attraction.address,
                'address': attraction.address,
                'description': attraction.description,
                'imageUrl': '',
                'homepageUrl': '',
                'phone': '',
                'longitude': attraction.longitude,
                'latitude': attraction.latitude,
                'startDate': None,
                'endDate': None,
            }
        )
    return items


def list_festivals_from_file(file_path: str) -> list[dict[str, str | None]]:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f'Festival data file not found: {file_path}')

    raw = json.loads(path.read_text(encoding='utf-8'))
    items = raw.get('items', []) if isinstance(raw, dict) else []
    festivals = [_normalize_festival_item(item) for item in items if isinstance(item, dict)]
    return [item for item in festivals if item.get('id') and item.get('title')]


def filter_festivals(
    festivals: list[dict[str, str | None]],
    *,
    keyword: str | None = None,
    status: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> list[dict[str, str | None]]:
    normalized_keyword = (keyword or '').strip().lower()
    normalized_status = (status or '').strip().lower()
    query_start = _to_date(start_date)
    query_end = _to_date(end_date)
    today = date.today()

    filtered: list[dict[str, str | None]] = []

    for festival in festivals:
        title = str(festival.get('title') or '').lower()
        description = str(festival.get('description') or '').lower()

        if normalized_keyword and normalized_keyword not in title and normalized_keyword not in description:
            continue

        festival_start = _to_date(festival.get('startDate'))
        festival_end = _to_date(festival.get('endDate')) or festival_start

        if normalized_status:
            festival_state = _festival_status(festival_start, festival_end, today)
            if festival_state != normalized_status:
                continue

        if query_start or query_end:
            if not festival_start:
                continue

            range_start = query_start or festival_start
            range_end = query_end or festival_end or festival_start
            active_end = festival_end or festival_start

            if festival_start > range_end or active_end < range_start:
                continue

        filtered.append(festival)

    return filtered


def list_festivals(
    *,
    root_dir: str,
    attractions: list[Attraction] | None = None,
    keyword: str | None = None,
    status: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> list[dict[str, str | None]]:
    festival_path = Path(root_dir) / 'data' / '서울_축제공연행사.json'
    if festival_path.exists():
        items = list_festivals_from_file(str(festival_path))
    else:
        items = _fallback_from_attractions(attractions or [])

    return filter_festivals(
        items,
        keyword=keyword,
        status=status,
        start_date=start_date,
        end_date=end_date,
    )
