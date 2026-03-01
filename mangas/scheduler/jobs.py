"""Scheduler jobs: chapter check and recommendation crawl."""
import logging
from urllib.parse import urlparse

import db.ops as ops
from crawler.registry import all_crawlers
from scrapers.registry import get_scraper
from utils.config_loader import load_config

logger = logging.getLogger(__name__)


def _domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lstrip("www.")
    except Exception:
        return ""


def run_chapter_check() -> dict:
    """Check all active manga for new chapters. Returns a summary dict."""
    config = load_config()
    enabled_sites = {
        site: cfg
        for site, cfg in config.get("sites", {}).items()
        if cfg.get("scraper", False)
    }
    enabled_domains: set[str] = set()
    for site_cfg in enabled_sites.values():
        for d in site_cfg.get("domains", []):
            enabled_domains.add(d)

    active = ops.get_all_active()
    updated = 0
    skipped = 0
    failed = 0

    for manga in active:
        domain = _domain(manga.url)
        if domain not in enabled_domains:
            skipped += 1
            continue

        scraper = get_scraper(domain)
        if scraper is None:
            logger.warning(f"No scraper for domain {domain!r} (manga id={manga.id})")
            skipped += 1
            continue

        try:
            chapter = scraper.check(manga.url)
            if chapter is not None:
                ops.update_published_chapter(manga.id, chapter)
                updated += 1
            else:
                failed += 1
        except Exception as e:
            logger.error(f"Error checking manga id={manga.id}: {e}")
            failed += 1

    logger.info(f"Chapter check done: {updated} updated, {skipped} skipped, {failed} failed")
    return {"updated": updated, "skipped": skipped, "failed": failed}


def run_recommendations() -> dict:
    """Crawl enabled sites for new recommendations."""
    config = load_config()
    rec_cfg = config.get("recommendations", {})
    min_chapters = rec_cfg.get("min_chapters", 100)
    max_pages = rec_cfg.get("max_pages", 5)  # guardrail
    themes = config.get("themes", [])
    enabled_sites = {
        site: cfg
        for site, cfg in config.get("sites", {}).items()
        if cfg.get("crawler", False)
    }
    enabled_domains: set[str] = set()
    for site_cfg in enabled_sites.values():
        for d in site_cfg.get("domains", []):
            enabled_domains.add(d)

    known_urls = ops.get_all_known_urls()
    excluded_titles = ops.get_all_non_active_titles()

    crawlers = [c for c in all_crawlers() if c.domain in enabled_domains]
    added = 0

    for crawler in crawlers:
        try:
            candidates = crawler.crawl(
                themes=themes,
                known_urls=known_urls,
                excluded_titles=excluded_titles,
                min_chapters=min_chapters,
                max_pages=max_pages,
            )
            for c in candidates:
                ops.upsert_recommendation(
                    url=c["url"],
                    title=c["title"],
                    site=c["site"],
                    chapter_count=c["chapter_count"],
                    matched_themes=c["matched_themes"],
                    score=c["score"],
                )
                added += 1
        except Exception as e:
            logger.error(f"Crawler {crawler.domain} failed: {e}")

    logger.info(f"Recommendations done: {added} candidates added/updated")
    return {"added": added}
