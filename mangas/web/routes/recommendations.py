import json

from flask import Blueprint, redirect, render_template, request, url_for

import db.ops as ops

bp = Blueprint("recommendations", __name__)


@bp.route("/recommendations")
def recommendations():
    recs = ops.get_unseen_recommendations()
    # Deserialise matched_themes JSON string for display
    for r in recs:
        try:
            r._themes_list = json.loads(r.matched_themes) if r.matched_themes else []
        except Exception:
            r._themes_list = []
    return render_template("recommendations.html", recs=recs)


@bp.route("/recommendations/<int:rec_id>/dismiss", methods=["POST"])
def dismiss(rec_id: int):
    ops.dismiss_recommendation(rec_id)
    return redirect(url_for("recommendations.recommendations"))
