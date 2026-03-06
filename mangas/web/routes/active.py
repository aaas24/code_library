import logging
from urllib.parse import urlparse

from flask import Blueprint, flash, redirect, render_template, request, url_for

import db.ops as ops
from web.routes.bugs import BUG_TYPES

logger = logging.getLogger(__name__)
bp = Blueprint("active", __name__)


def _title_from_url(url: str) -> str:
    """Extract a readable title from a manga URL slug."""
    try:
        path = urlparse(url).path.rstrip("/")
        slug = path.split("/")[-1]
        return slug.replace("-", " ").replace("_", " ").title()
    except Exception:
        return url


def _sort_key(m):
    pending = (m.last_episode_published or 0) - (m.last_episode_read or 0)
    last_read_ts = m.last_read_at.timestamp() if m.last_read_at else 0
    return (
        not m.is_favorite,   # favorites first (False < True)
        -last_read_ts,       # most recently read first
        -pending,            # most pending chapters first
    )


@bp.route("/active")
def active():
    manga_list = [m for m in ops.get_all_active() if m.bug_type != "url_broken"]
    manga_list.sort(key=_sort_key)
    for m in manga_list:
        m.display_title = m.title or _title_from_url(m.url)
        m.bug_label = BUG_TYPES.get(m.bug_type) if m.bug_type else None
    return render_template("active.html", manga_list=manga_list, bug_types=BUG_TYPES)


@bp.route("/active/update-read", methods=["POST"])
def update_read():
    manga_id = request.form.get("manga_id", type=int)
    chapter = request.form.get("chapter", type=int)
    if manga_id is not None and chapter is not None:
        ops.mark_chapter_read(manga_id, chapter)
        logger.info(f"Manually updated read chapter: manga_id={manga_id} chapter={chapter}")
    return redirect(url_for("active.active"))


@bp.route("/active/toggle-favorite", methods=["POST"])
def toggle_favorite():
    manga_id = request.form.get("manga_id", type=int)
    if manga_id is not None:
        ops.toggle_favorite(manga_id)
        logger.info(f"Toggled favorite: manga_id={manga_id}")
    return redirect(url_for("active.active"))



@bp.route("/active/retire", methods=["POST"])
def retire():
    manga_id = request.form.get("manga_id", type=int)
    status = request.form.get("status")
    if manga_id is not None and status in ("finished", "skip"):
        ops.retire_manga(manga_id, status)
        logger.info(f"Retired manga: manga_id={manga_id} status={status!r}")
    return redirect(url_for("active.active"))


@bp.route("/active/set-bug", methods=["POST"])
def set_bug():
    manga_id = request.form.get("manga_id", type=int)
    bug_type = request.form.get("bug_type")
    if manga_id is not None and bug_type in BUG_TYPES:
        ops.set_bug(manga_id, bug_type)
        logger.info(f"Bug flagged from active: manga_id={manga_id} bug_type={bug_type!r}")
    return redirect(url_for("active.active"))


@bp.route("/active/clear-bug", methods=["POST"])
def clear_bug():
    manga_id = request.form.get("manga_id", type=int)
    if manga_id is not None:
        ops.clear_bug(manga_id)
        logger.info(f"Bug cleared from active: manga_id={manga_id}")
    return redirect(url_for("active.active"))


def _extract_title(soup, url: str) -> str:
    """Best-effort title extraction: og:title → h1 → URL slug."""
    og = soup.find("meta", property="og:title")
    if og and og.get("content", "").strip():
        return og["content"].strip()
    h1 = soup.find("h1")
    if h1:
        text = h1.get_text(strip=True)
        if text:
            return text
    return _title_from_url(url)


@bp.route("/active/add", methods=["POST"])
def add_manga():
    url = request.form.get("url", "").strip()
    if not url:
        flash("Please enter a URL.", "error")
        return redirect(url_for("active.active"))

    domain = urlparse(url).netloc.lstrip("www.")

    from scrapers.registry import get_scraper
    from utils.onboard_site import auto_detect_selector, CANDIDATE_SELECTORS, _extract_number_from_text

    scraper = get_scraper(domain)

    if scraper:
        # Known site — use existing scraper
        soup = scraper.fetch(url)
        title = _extract_title(soup, url) if soup else _title_from_url(url)
        chapter = scraper.get_latest_chapter(soup) if soup else None
        manga = ops.upsert_manga(url=url, title=title, last_episode_published=chapter)
        msg = f"Added \"{title}\""
        if chapter:
            msg += f" — latest chapter: {chapter}"
        logger.info(f"Added manga via URL: manga_id={manga.id} domain={domain} chapter={chapter}")
        flash(msg, "success")
    else:
        # Unknown site — best-effort using generic selector detection
        import requests as _req
        from bs4 import BeautifulSoup
        _HEADERS = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        }
        soup = None
        try:
            resp = _req.get(url, headers=_HEADERS, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "lxml")
        except Exception as exc:
            logger.warning(f"Failed to fetch {url}: {exc}")

        title = _extract_title(soup, url) if soup else _title_from_url(url)
        chapter = None
        selector = None
        if soup:
            selector, chapter_str = auto_detect_selector(soup)
            if chapter_str:
                try:
                    chapter = int(float(chapter_str))
                except ValueError:
                    pass

        manga = ops.upsert_manga(url=url, title=title, last_episode_published=chapter)
        ops.set_bug(manga.id, "no_scraper")
        logger.info(
            f"Added manga from unknown site: manga_id={manga.id} domain={domain} "
            f"chapter={chapter} detected_selector={selector!r}"
        )

        if selector:
            flash(
                f"Added \"{title}\" — no scraper for {domain}. "
                f"Detected selector: {selector!r} (chapter {chapter}). "
                f"Add a scraper in scrapers/{domain.split('.')[0]}.py to track updates.",
                "warning",
            )
        else:
            flash(
                f"Added \"{title}\" — no scraper for {domain} and no chapter selector detected. "
                f"Add a scraper in scrapers/{domain.split('.')[0]}.py to track updates.",
                "warning",
            )

    return redirect(url_for("active.active"))
