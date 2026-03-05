from flask import Blueprint, redirect, render_template, url_for

import db.ops as ops

bp = Blueprint("dashboard", __name__)


@bp.route("/")
def index():
    return redirect(url_for("active.active"))


@bp.route("/home")
def home():
    update_count = len(ops.get_manga_with_updates())
    rec_count = len(ops.get_unseen_recommendations())
    return render_template("dashboard.html", update_count=update_count, rec_count=rec_count)
