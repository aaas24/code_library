from urllib.parse import urlparse

from flask import Blueprint, render_template

import db.ops as ops

bp = Blueprint("updates", __name__)


def _title_from_url(url: str) -> str:
    try:
        path = urlparse(url).path.rstrip("/")
        slug = path.split("/")[-1]
        return slug.replace("-", " ").replace("_", " ").title()
    except Exception:
        return url


@bp.route("/updates")
def updates():
    manga_list = []
    for m in ops.get_manga_with_updates():
        pending = (m.last_episode_published or 0) - (m.last_episode_read or 0)
        if pending > 5:
            m.pending = pending
            m.display_title = m.title or _title_from_url(m.url)
            manga_list.append(m)
    manga_list.sort(key=lambda m: (not m.is_favorite, -m.pending))
    return render_template("updates.html", manga_list=manga_list)
