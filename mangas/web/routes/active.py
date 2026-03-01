from flask import Blueprint, render_template

import db.ops as ops

bp = Blueprint("active", __name__)


@bp.route("/active")
def active():
    manga_list = ops.get_all_active()
    return render_template("active.html", manga_list=manga_list)
