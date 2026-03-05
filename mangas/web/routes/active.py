import logging

from flask import Blueprint, redirect, render_template, request, url_for

import db.ops as ops

logger = logging.getLogger(__name__)
bp = Blueprint("active", __name__)


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
