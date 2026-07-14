from __future__ import annotations

import json
from pathlib import Path

from app.models.attraction import Attraction


def _extract_district(addr1: str) -> str:
    parts = [part for part in addr1.split() if part]
    if len(parts) >= 2 and parts[0].startswith('서울'):
        return parts[1]
    return '서울'


def _normalize_festival_item(item: dict) -> dict[str, str | None]:
    addr1 = str(item.get('addr1', '')).strip()
    addr2 = str(item.get('addr2', '')).strip()
    address = ' '.join(part for part in [addr1, addr2] if part).strip()
    phone = str(item.get('tel', '')).strip()
    place = addr2 or addr1
    region = _extract_district(addr1)

    description_parts = []
    if place and place != address:
        description_parts.append(f'장소: {place}')
    if phone:
        description_parts.append(f'문의: {phone}')
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
        'startDate': None,
        'endDate': None,
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


def list_festivals(*, root_dir: str, attractions: list[Attraction] | None = None) -> list[dict[str, str | None]]:
    festival_path = Path(root_dir) / 'data' / '서울_축제공연행사.json'
    if festival_path.exists():
        return list_festivals_from_file(str(festival_path))
    return _fallback_from_attractions(attractions or [])