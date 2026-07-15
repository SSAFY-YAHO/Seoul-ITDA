from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.attraction import Attraction


CONTENT_TYPE_MAP: dict[str, str] = {
    '12': '관광지',
    '14': '문화시설',
    '15': '축제공연행사',
    '25': '여행코스',
    '28': '레포츠',
    '32': '숙박',
    '38': '쇼핑',
    '39': '음식점',
}


def _extract_district(addr1: str) -> str:
    parts = [part for part in addr1.split() if part]
    if len(parts) >= 2 and parts[0].startswith('서울'):
        return parts[1]
    return '미상'


def _to_float(value: object) -> float | None:
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return None


def _normalize_items(raw: object) -> tuple[list[dict], str]:
    if isinstance(raw, dict) and isinstance(raw.get('items'), list):
        content_type = str(raw.get('contentType', '')).strip()
        return [item for item in raw['items'] if isinstance(item, dict)], content_type

    if isinstance(raw, list):
        return [item for item in raw if isinstance(item, dict)], ''

    if isinstance(raw, dict) and isinstance(raw.get('data'), list):
        return [item for item in raw['data'] if isinstance(item, dict)], ''

    return [], ''


def _list_data_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if path.is_dir():
        files = sorted(path.glob('서울_*.json'))
        if files:
            return files
        return sorted(path.glob('*.json'))
    return []


def load_attractions_from_file(db: Session, file_path: str) -> dict[str, int | str]:
    path = Path(file_path)

    files = _list_data_files(path)
    if not files:
        raise FileNotFoundError(f'Data file not found: {file_path}')

    loaded = 0
    updated = 0
    skipped = 0

    for json_file in files:
        raw = json.loads(json_file.read_text(encoding='utf-8'))
        items, top_content_type = _normalize_items(raw)

        for item in items:
            content_id = str(item.get('contentid', '')).strip()
            content_type_id = str(item.get('contenttypeid', '')).strip()
            source_id = f'{content_type_id}:{content_id}' if content_type_id else content_id
            name = str(item.get('title', '')).strip()
            addr1 = str(item.get('addr1', '')).strip()
            addr2 = str(item.get('addr2', '')).strip()
            tel = str(item.get('tel', '')).strip()
            image_url = str(item.get('firstimage', '')).strip()
            thumbnail_url = str(item.get('firstimage2', '')).strip()
            longitude = _to_float(item.get('mapx'))
            latitude = _to_float(item.get('mapy'))

            if not source_id or not name:
                skipped += 1
                continue

            category = top_content_type or CONTENT_TYPE_MAP.get(content_type_id, '기타')
            district = _extract_district(addr1)
            address = ' '.join(part for part in [addr1, addr2] if part).strip()
            description_parts = [part for part in [addr1, addr2, tel] if part]
            description = ' / '.join(description_parts) if description_parts else '설명 정보 없음'

            tags = ','.join(
                [
                    category,
                    str(item.get('cat1', '')).strip(),
                    str(item.get('cat2', '')).strip(),
                    str(item.get('cat3', '')).strip(),
                    str(item.get('lclsSystm1', '')).strip(),
                    str(item.get('lclsSystm2', '')).strip(),
                    str(item.get('lclsSystm3', '')).strip(),
                ]
            )
            tags = ','.join(part for part in tags.split(',') if part)

            attraction = db.query(Attraction).filter(Attraction.source_id == source_id).first()
            if attraction is None:
                attraction = Attraction(
                    source_id=source_id,
                    name=name,
                    category=category,
                    district=district,
                    description=description,
                    address=address,
                    tags=tags,
                    image_url=image_url,
                    thumbnail_url=thumbnail_url,
                    telephone=tel,
                    longitude=longitude,
                    latitude=latitude,
                )
                db.add(attraction)
                loaded += 1
            else:
                attraction.name = name
                attraction.category = category
                attraction.district = district
                attraction.description = description
                attraction.address = address
                attraction.tags = tags
                attraction.image_url = image_url
                attraction.thumbnail_url = thumbnail_url
                attraction.telephone = tel
                attraction.longitude = longitude
                attraction.latitude = latitude
                updated += 1

    db.commit()

    return {
        'message': 'Seoul TourAPI data load completed',
        'loaded': loaded,
        'updated': updated,
        'skipped': skipped,
        'processed_files': len(files),
        'file_path': str(path),
    }


def list_attractions(
    db: Session,
    *,
    q: str | None = None,
    category: str | None = None,
    district: str | None = None,
    limit: int = 12,
) -> list[Attraction]:
    query = db.query(Attraction)

    if q:
        keyword = f'%{q.strip()}%'
        query = query.filter(
            Attraction.name.ilike(keyword)
            | Attraction.description.ilike(keyword)
            | Attraction.address.ilike(keyword)
            | Attraction.tags.ilike(keyword)
        )

    if category:
        query = query.filter(Attraction.category.ilike(f'%{category.strip()}%'))

    if district:
        query = query.filter(Attraction.district.ilike(f'%{district.strip()}%'))

    return (
        query.order_by(Attraction.updated_at.desc(), Attraction.id.desc())
        .limit(max(1, min(limit, 50)))
        .all()
    )
