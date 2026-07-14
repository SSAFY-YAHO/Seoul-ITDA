from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.attraction import Attraction


def _normalize_items(raw: object) -> list[dict]:
    if isinstance(raw, list):
        return [item for item in raw if isinstance(item, dict)]
    if isinstance(raw, dict) and isinstance(raw.get('items'), list):
        return [item for item in raw['items'] if isinstance(item, dict)]
    return []


def load_attractions_from_file(db: Session, file_path: str) -> dict[str, int | str]:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f'Data file not found: {file_path}')

    raw = json.loads(path.read_text(encoding='utf-8'))
    items = _normalize_items(raw)

    loaded = 0
    updated = 0
    skipped = 0

    for item in items:
        source_id = str(item.get('source_id', '')).strip()
        name = str(item.get('name', '')).strip()
        category = str(item.get('category', '')).strip()
        district = str(item.get('district', '')).strip()
        description = str(item.get('description', '')).strip()
        address = str(item.get('address', '')).strip()
        tags_raw = item.get('tags', [])

        if not source_id or not name or not category or not district:
            skipped += 1
            continue

        if isinstance(tags_raw, list):
            tags = ','.join(str(tag).strip() for tag in tags_raw if str(tag).strip())
        else:
            tags = str(tags_raw).strip()

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
            updated += 1

    db.commit()

    return {
        'message': 'Seoul data load completed',
        'loaded': loaded,
        'updated': updated,
        'skipped': skipped,
        'file_path': str(path),
    }
