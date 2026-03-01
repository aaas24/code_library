from flask import Blueprint, abort, redirect

import db.ops as ops

bp = Blueprint("read", __name__)


@bp.route("/read/<int:manga_id>/<int:chapter>")
def read(manga_id: int, chapter: int):
    """Log the read chapter and redirect to the manga's external URL."""
    manga = ops.mark_chapter_read(manga_id, chapter)
    if manga is None:
        abort(404)
    return redirect(manga.url)
