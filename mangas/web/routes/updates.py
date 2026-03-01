from flask import Blueprint, render_template

import db.ops as ops

bp = Blueprint("updates", __name__)


@bp.route("/updates")
def updates():
    manga_list = ops.get_manga_with_updates()
    return render_template("updates.html", manga_list=manga_list)
