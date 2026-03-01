from flask import Blueprint, render_template

import db.ops as ops

bp = Blueprint("dashboard", __name__)


@bp.route("/")
def index():
    update_count = len(ops.get_manga_with_updates())
    rec_count = len(ops.get_unseen_recommendations())
    return render_template("dashboard.html", update_count=update_count, rec_count=rec_count)
