import logging

from flask import Blueprint, redirect, render_template, request, url_for

import db.ops as ops

logger = logging.getLogger(__name__)
bp = Blueprint("active", __name__)


@bp.route("/active")
def active():
    manga_list = ops.get_all_active()
    return render_template("active.html", manga_list=manga_list)


@bp.route("/active/update-read", methods=["POST"])
def update_read():
    manga_id = request.form.get("manga_id", type=int)
    chapter = request.form.get("chapter", type=int)
    if manga_id is not None and chapter is not None:
        ops.mark_chapter_read(manga_id, chapter)
        logger.info(f"Manually updated read chapter: manga_id={manga_id} chapter={chapter}")
    return redirect(url_for("active.active"))
