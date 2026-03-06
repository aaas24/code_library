import logging
import re

from flask import Blueprint, redirect, render_template, request, session, url_for

import db.ops as ops
from crawler.registry import all_crawlers


def _title_from_url(url: str) -> str:
    from urllib.parse import urlparse
    try:
        path = urlparse(url).path.rstrip("/")
        slug = path.split("/")[-1]
        return slug.replace("-", " ").replace("_", " ").title()
    except Exception:
        return url

logger = logging.getLogger(__name__)
bp = Blueprint("bugs", __name__)

BUG_TYPES = {
    "url_broken": "URL broken",
    "chapter_not_updated": "Latest chapter not displayed",
    "wrong_title": "Wrong title",
    "no_scraper": "No scraper",
    "duplicate": "Duplicate entry",
    "other": "Other",
}


@bp.route("/bugs")
def bugs():
    manga_list = ops.get_manga_with_bugs()
    for m in manga_list:
        m.display_title = m.title or _title_from_url(m.url)
        m.bug_label = BUG_TYPES.get(m.bug_type, m.bug_type)
    candidates = session.pop("url_candidates", {})
    all_active = ops.get_all_active()
    for m in all_active:
        m.display_title = m.title or _title_from_url(m.url)
    return render_template(
        "bugs.html",
        manga_list=manga_list,
        bug_types=BUG_TYPES,
        candidates=candidates,
        all_active=all_active,
    )


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


@bp.route("/bugs/<int:manga_id>/find-url", methods=["POST"])
def find_url(manga_id: int):
    manga = ops.get_manga_by_id(manga_id)
    if manga is None:
        return redirect(url_for("bugs.bugs"))
    title = manga.title or manga.url
    results = []
    seen_urls: set[str] = set()
    for crawler in all_crawlers():
        try:
            for item in crawler.search_by_title(title):
                if item.get("url") and item["url"] not in seen_urls:
                    seen_urls.add(item["url"])
                    results.append({
                        "url": item["url"],
                        "title": item.get("title") or "",
                        "chapter_count": item.get("chapter_count") or 0,
                        "site": crawler.domain,
                    })
        except Exception:
            pass
    session["url_candidates"] = {str(manga_id): results}
    logger.info(f"find-url: manga_id={manga_id} title={title!r} found {len(results)} candidates")
    return redirect(url_for("bugs.bugs"))


@bp.route("/bugs/<int:manga_id>/update-url", methods=["POST"])
def update_url(manga_id: int):
    new_url = request.form.get("new_url", "").strip()
    if manga_id and new_url:
        ops.update_manga_url(manga_id, new_url)
        logger.info(f"URL updated: manga_id={manga_id} new_url={new_url!r}")
    return redirect(url_for("bugs.bugs"))


@bp.route("/bugs/<int:manga_id>/fix-title", methods=["POST"])
def fix_title(manga_id: int):
    new_title = request.form.get("new_title", "").strip()
    if not new_title:
        return redirect(url_for("bugs.bugs"))
    manga = ops.get_manga_by_id(manga_id)
    if manga is None:
        return redirect(url_for("bugs.bugs"))
    old_title = manga.title
    ops.update_manga_title(manga_id, new_title)
    logger.info(f"Title corrected: manga_id={manga_id} old={old_title!r} new={new_title!r}")
    # Best-effort crawler diagnosis: find which HTML element contains the correct title
    try:
        from crawler.registry import get_crawler
        from urllib.parse import urlparse
        domain = urlparse(manga.url).netloc.lstrip("www.")
        crawler = get_crawler(domain)
        if crawler:
            soup = crawler.fetch(manga.url)
            if soup:
                pattern = re.compile(re.escape(new_title), re.I)
                for el in soup.find_all(string=pattern):
                    parent = el.parent
                    if parent:
                        path_parts = []
                        for ancestor in reversed(list(parent.parents)[:4]):
                            tag = getattr(ancestor, "name", None)
                            if tag and tag not in ("[document]", "html", "body"):
                                cls = " ".join(ancestor.get("class", []))
                                path_parts.append(f"{tag}.{cls}" if cls else tag)
                        tag_name = parent.name
                        cls = " ".join(parent.get("class", []))
                        path_parts.append(f"{tag_name}.{cls}" if cls else tag_name)
                        selector_path = " > ".join(path_parts)
                        logger.info(
                            f"Title diagnosis manga_id={manga_id} domain={domain}: "
                            f"'{new_title}' found in [{selector_path}]"
                        )
    except Exception as exc:
        logger.debug(f"Title diagnosis failed for manga_id={manga_id}: {exc}")
    return redirect(url_for("bugs.bugs"))


@bp.route("/bugs/<int:manga_id>/merge-into", methods=["POST"])
def merge_into(manga_id: int):
    keep_id = request.form.get("keep_id", type=int)
    if keep_id is not None and keep_id != manga_id:
        ops.merge_manga(keep_id, manga_id)
        logger.info(f"Merged duplicate: retire_id={manga_id} keep_id={keep_id}")
    return redirect(url_for("bugs.bugs"))
