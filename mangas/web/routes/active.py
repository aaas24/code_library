import logging
from urllib.parse import urlparse

from flask import Blueprint, redirect, render_template, request, url_for

import db.ops as ops

logger = logging.getLogger(__name__)
bp = Blueprint("active", __name__)


def _title_from_url(url: str) -> str:
    """Extract a readable title from a manga URL slug."""
    try:
        path = urlparse(url).path.rstrip("/")
        slug = path.split("/")[-1]
        return slug.replace("-", " ").replace("_", " ").title()
    except Exception:
        return url


def _sort_key(m):
    pending = (m.last_episode_published or 0) - (m.last_episode_read or 0)
    last_read_ts = m.last_read_at.timestamp() if m.last_read_at else 0
    return (
        not m.is_favorite,   # favorites first (False < True)
        -last_read_ts,       # most recently read first
        -pending,            # most pending chapters first
    )


@bp.route("/active")
def active():
    manga_list = ops.get_all_active()
    manga_list.sort(key=_sort_key)
    for m in manga_list:
        m.display_title = m.title or _title_from_url(m.url)
    return render_template("active.html", manga_list=manga_list)


@bp.route("/active/update-read", methods=["POST"])
def update_read():
    manga_id = request.form.get("manga_id", type=int)
    chapter = request.form.get("chapter", type=int)
    if manga_id is not None and chapter is not None:
        ops.mark_chapter_read(manga_id, chapter)
        logger.info(f"Manually updated read chapter: manga_id={manga_id} chapter={chapter}")
    return redirect(url_for("active.active"))


@bp.route("/active/toggle-favorite", methods=["POST"])
def toggle_favorite():
    manga_id = request.form.get("manga_id", type=int)
    if manga_id is not None:
        ops.toggle_favorite(manga_id)
        logger.info(f"Toggled favorite: manga_id={manga_id}")
    return redirect(url_for("active.active"))


@bp.route("/active/retire", methods=["POST"])
def retire():
    manga_id = request.form.get("manga_id", type=int)
    status = request.form.get("status")
    if manga_id is not None and status in ("finished", "skip"):
        ops.retire_manga(manga_id, status)
        logger.info(f"Retired manga: manga_id={manga_id} status={status!r}")
    return redirect(url_for("active.active"))
