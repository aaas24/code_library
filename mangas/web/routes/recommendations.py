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
        ops.upsert_manga(url=rec.url, title=rec.title, status="active")
        ops.dismiss_recommendation(rec_id)
        logger.info(f"Added recommendation to active list: rec_id={rec_id} title={rec.title!r}")
    return redirect(url_for("recommendations.recommendations"))


@bp.route("/recommendations/<int:rec_id>/ignore", methods=["POST"])
def ignore(rec_id: int):
    """Dismiss a recommendation permanently."""
    ops.dismiss_recommendation(rec_id)
    logger.info(f"Ignored recommendation: rec_id={rec_id}")
    return redirect(url_for("recommendations.recommendations"))
