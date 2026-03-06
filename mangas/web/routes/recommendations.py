import json
import logging

from flask import Blueprint, redirect, render_template, request, url_for

import db.ops as ops

logger = logging.getLogger(__name__)
bp = Blueprint("recommendations", __name__)


@bp.route("/recommendations")
def recommendations():
    recs = ops.get_unseen_recommendations()
    for r in recs:
        try:
            r._themes_list = json.loads(r.matched_themes) if r.matched_themes else []
        except Exception:
            r._themes_list = []
    return render_template("recommendations.html", recs=recs)


@bp.route("/recommendations/<int:rec_id>/add", methods=["POST"])
def add_to_active(rec_id: int):
    """Add a recommendation to the active reading list and dismiss it."""
    rec = ops.get_recommendation_by_id(rec_id)
    if rec:
        chapter_read = request.form.get("chapter_read", type=int)
        status = request.form.get("status", "active")
        if status not in ("active", "finished"):
            status = "active"
        manga = ops.upsert_manga(url=rec.url, title=rec.title, status=status)
        if chapter_read is not None and manga:
            ops.mark_chapter_read(manga.id, chapter_read)
        ops.dismiss_recommendation(rec_id)
        logger.info(f"Added recommendation: rec_id={rec_id} title={rec.title!r} status={status} chapter_read={chapter_read}")
    return redirect(url_for("recommendations.recommendations"))


@bp.route("/recommendations/<int:rec_id>/ignore", methods=["POST"])
def ignore(rec_id: int):
    """Dismiss a recommendation permanently."""
    ops.dismiss_recommendation(rec_id)
    logger.info(f"Ignored recommendation: rec_id={rec_id}")
    return redirect(url_for("recommendations.recommendations"))
