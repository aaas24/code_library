import logging

from flask import Blueprint, redirect, render_template, request, url_for

import db.ops as ops

logger = logging.getLogger(__name__)
bp = Blueprint("bugs", __name__)

BUG_TYPES = {
    "url_broken": "URL broken",
    "chapter_not_updated": "Latest chapter not displayed",
    "wrong_title": "Wrong title",
    "other": "Other",
}


@bp.route("/bugs")
def bugs():
    manga_list = ops.get_manga_with_bugs()
    for m in manga_list:
        m.display_title = m.title or m.url
        m.bug_label = BUG_TYPES.get(m.bug_type, m.bug_type)
    return render_template("bugs.html", manga_list=manga_list, bug_types=BUG_TYPES)


@bp.route("/bugs/set", methods=["POST"])
def set_bug():
    manga_id = request.form.get("manga_id", type=int)
    bug_type = request.form.get("bug_type")
    if manga_id is not None and bug_type in BUG_TYPES:
        ops.set_bug(manga_id, bug_type)
        logger.info(f"Bug flagged: manga_id={manga_id} bug_type={bug_type!r}")
    return redirect(url_for("bugs.bugs"))


@bp.route("/bugs/clear", methods=["POST"])
def clear_bug():
    manga_id = request.form.get("manga_id", type=int)
    if manga_id is not None:
        ops.clear_bug(manga_id)
        logger.info(f"Bug cleared: manga_id={manga_id}")
    return redirect(url_for("bugs.bugs"))
