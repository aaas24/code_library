"""All DB read/write operations. Every write triggers a JSON export."""
import json
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from db.export import export_to_json
from db.models import Manga, Recommendation, get_engine, get_session, init_db

# Module-level engine — callers may override via init()
_engine = None


def init(db_path: str = "data/mangas.db"):
    global _engine
    _engine = init_db(db_path)
    return _engine


def _get_session() -> Session:
    if _engine is None:
        init()
    return get_session(_engine)


def _domain_from_url(url: str) -> str:
    try:
        return urlparse(url).netloc.lstrip("www.")
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# Manga writes
# ---------------------------------------------------------------------------


def upsert_manga(
    url: str,
    title: Optional[str] = None,
    status: str = "active",
    last_episode_published: Optional[int] = None,
    last_episode_read: Optional[int] = None,
    raw_note: Optional[str] = None,
) -> Manga:
    """Insert or update a manga record. Triggers JSON export on every call."""
    session = _get_session()
    try:
        manga = session.query(Manga).filter_by(url=url).first()
        if manga is None:
            manga = Manga(
                url=url,
                title=title,
                site=_domain_from_url(url),
                status=status,
                last_episode_published=last_episode_published,
                last_episode_read=last_episode_read,
                raw_note=raw_note,
            )
            session.add(manga)
        else:
            # Keep the richer value for title
            if title and not manga.title:
                manga.title = title
            # Only update status if being demoted (never promote)
            if status != "active":
                manga.status = status
            # Take the higher chapter numbers
            if last_episode_published is not None:
                if manga.last_episode_published is None or last_episode_published > manga.last_episode_published:
                    manga.last_episode_published = last_episode_published
            if last_episode_read is not None:
                if manga.last_episode_read is None or last_episode_read > manga.last_episode_read:
                    manga.last_episode_read = last_episode_read
            if raw_note and not manga.raw_note:
                manga.raw_note = raw_note

        _refresh_has_update(manga)
        session.commit()
        session.refresh(manga)
        export_to_json(session)
        return manga
    finally:
        session.close()


_BUG_TYPES = {"url_broken", "chapter_not_updated", "wrong_title", "other"}


def set_bug(manga_id: int, bug_type: str) -> Optional[Manga]:
    """Flag a manga with a bug type."""
    if bug_type not in _BUG_TYPES:
        raise ValueError(f"Invalid bug_type: {bug_type!r}")
    session = _get_session()
    try:
        manga = session.query(Manga).filter_by(id=manga_id).first()
        if manga is None:
            return None
        manga.bug_type = bug_type
        session.commit()
        session.refresh(manga)
        export_to_json(session)
        return manga
    finally:
        session.close()


def clear_bug(manga_id: int) -> Optional[Manga]:
    """Remove a bug flag from a manga."""
    session = _get_session()
    try:
        manga = session.query(Manga).filter_by(id=manga_id).first()
        if manga is None:
            return None
        manga.bug_type = None
        session.commit()
        session.refresh(manga)
        export_to_json(session)
        return manga
    finally:
        session.close()


def get_manga_with_bugs() -> list[Manga]:
    """Return all active manga that have a bug flag set."""
    session = _get_session()
    try:
        return (
            session.query(Manga)
            .filter(Manga.status == "active", Manga.bug_type.isnot(None))
            .order_by(Manga.bug_type)
            .all()
        )
    finally:
        session.close()


def retire_manga(manga_id: int, status: str) -> Optional[Manga]:
    """Set a manga's status to 'finished' or 'skip', removing it from the active list."""
    if status not in ("finished", "skip"):
        raise ValueError(f"Invalid retire status: {status!r}")
    session = _get_session()
    try:
        manga = session.query(Manga).filter_by(id=manga_id).first()
        if manga is None:
            return None
        manga.status = status
        session.commit()
        session.refresh(manga)
        export_to_json(session)
        return manga
    finally:
        session.close()


def toggle_favorite(manga_id: int) -> Optional[Manga]:
    """Flip the is_favorite flag."""
    session = _get_session()
    try:
        manga = session.query(Manga).filter_by(id=manga_id).first()
        if manga is None:
            return None
        manga.is_favorite = not manga.is_favorite
        session.commit()
        session.refresh(manga)
        export_to_json(session)
        return manga
    finally:
        session.close()


def update_published_chapter(manga_id: int, chapter: int) -> Optional[Manga]:
    """Update last_episode_published from a scraper result."""
    session = _get_session()
    try:
        manga = session.query(Manga).filter_by(id=manga_id).first()
        if manga is None:
            return None
        manga.last_episode_published = chapter
        manga.last_checked = datetime.now(timezone.utc)
        _refresh_has_update(manga)
        session.commit()
        session.refresh(manga)
        export_to_json(session)
        return manga
    finally:
        session.close()


def mark_chapter_read(manga_id: int, chapter: int) -> Optional[Manga]:
    """Update last_episode_read (called from /read/ redirect route)."""
    session = _get_session()
    try:
        manga = session.query(Manga).filter_by(id=manga_id).first()
        if manga is None:
            return None
        manga.last_episode_read = chapter
        manga.last_read_at = datetime.now(timezone.utc)
        _refresh_has_update(manga)
        session.commit()
        session.refresh(manga)
        export_to_json(session)
        return manga
    finally:
        session.close()


def _refresh_has_update(manga: Manga) -> None:
    pub = manga.last_episode_published
    read = manga.last_episode_read
    if pub is not None and read is not None:
        manga.has_update = pub > read
    elif pub is not None and read is None:
        manga.has_update = True
    else:
        manga.has_update = False


# ---------------------------------------------------------------------------
# Manga reads
# ---------------------------------------------------------------------------


def get_all_active() -> list[Manga]:
    session = _get_session()
    try:
        return session.query(Manga).filter_by(status="active").all()
    finally:
        session.close()


def get_manga_with_updates() -> list[Manga]:
    session = _get_session()
    try:
        return (
            session.query(Manga)
            .filter(Manga.status == "active", Manga.has_update.is_(True))
            .all()
        )
    finally:
        session.close()


def get_all_known_urls() -> set[str]:
    session = _get_session()
    try:
        rows = session.query(Manga.url).all()
        return {r.url for r in rows}
    finally:
        session.close()


def get_manga_by_id(manga_id: int) -> Optional[Manga]:
    session = _get_session()
    try:
        return session.query(Manga).filter_by(id=manga_id).first()
    finally:
        session.close()


# ---------------------------------------------------------------------------
# Recommendation writes
# ---------------------------------------------------------------------------


def upsert_recommendation(
    url: str,
    title: Optional[str],
    site: str,
    chapter_count: int,
    matched_themes: list[str],
    score: int,
) -> Recommendation:
    session = _get_session()
    try:
        rec = session.query(Recommendation).filter_by(url=url).first()
        if rec is None:
            rec = Recommendation(
                url=url,
                title=title,
                site=site,
                chapter_count=chapter_count,
                matched_themes=json.dumps(matched_themes),
                score=score,
                seen=False,
                discovered_at=datetime.now(timezone.utc),
            )
            session.add(rec)
        else:
            rec.score = score
            rec.matched_themes = json.dumps(matched_themes)
            rec.chapter_count = chapter_count
        session.commit()
        session.refresh(rec)
        export_to_json(session)
        return rec
    finally:
        session.close()


def dismiss_recommendation(rec_id: int) -> Optional[Recommendation]:
    session = _get_session()
    try:
        rec = session.query(Recommendation).filter_by(id=rec_id).first()
        if rec is None:
            return None
        rec.seen = True
        session.commit()
        session.refresh(rec)
        export_to_json(session)
        return rec
    finally:
        session.close()


# ---------------------------------------------------------------------------
# Recommendation reads
# ---------------------------------------------------------------------------


def get_recommendation_by_id(rec_id: int) -> Optional[Recommendation]:
    session = _get_session()
    try:
        return session.query(Recommendation).filter_by(id=rec_id).first()
    finally:
        session.close()


def get_unseen_recommendations() -> list[Recommendation]:
    session = _get_session()
    try:
        return (
            session.query(Recommendation)
            .filter_by(seen=False)
            .order_by(Recommendation.score.desc())
            .all()
        )
    finally:
        session.close()


def get_all_non_active_titles() -> set[str]:
    """Return lowercase titles from manga with status != active (for filtering)."""
    session = _get_session()
    try:
        rows = (
            session.query(Manga.title)
            .filter(Manga.status != "active")
            .all()
        )
        return {r.title.lower() for r in rows if r.title}
    finally:
        session.close()
