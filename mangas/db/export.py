"""Auto-exports DB contents to data/mangas.json after every write."""
import json
import os
from pathlib import Path


def export_to_json(session, json_path: str = "data/mangas.json") -> None:
    """Write all manga and recommendation rows to a human-readable JSON file."""
    # Lazy import to avoid circular
    from db.models import Manga, Recommendation

    Path(json_path).parent.mkdir(parents=True, exist_ok=True)

    mangas = [_manga_to_dict(m) for m in session.query(Manga).all()]
    recommendations = [_rec_to_dict(r) for r in session.query(Recommendation).all()]

    data = {"manga": mangas, "recommendations": recommendations}
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def _manga_to_dict(m) -> dict:
    return {
        "id": m.id,
        "url": m.url,
        "title": m.title,
        "site": m.site,
        "last_episode_published": m.last_episode_published,
        "last_episode_read": m.last_episode_read,
        "status": m.status,
        "has_update": m.has_update,
        "last_checked": str(m.last_checked) if m.last_checked else None,
        "raw_note": m.raw_note,
    }


def _rec_to_dict(r) -> dict:
    return {
        "id": r.id,
        "url": r.url,
        "title": r.title,
        "site": r.site,
        "chapter_count": r.chapter_count,
        "matched_themes": r.matched_themes,
        "score": r.score,
        "seen": r.seen,
        "discovered_at": str(r.discovered_at) if r.discovered_at else None,
    }
