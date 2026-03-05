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

    logger.info(f"Chapter check starting — enabled scraper domains: {sorted(enabled_domains)}")

    active = ops.get_all_active()
    logger.info(f"Active manga in DB: {len(active)}")

    if not active:
        logger.info("No active manga to check — add manga via the import script first")
        return {"updated": 0, "skipped": 0, "failed": 0}

    updated = 0
    skipped = 0
    failed = 0

    for manga in active:
        domain = _domain(manga.url)
        if domain not in enabled_domains:
            logger.debug(f"Skipping manga id={manga.id} ({domain!r}) — domain not in enabled scrapers")
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
                logger.info(f"Updated manga id={manga.id}: latest chapter={chapter}")
                updated += 1
            else:
                logger.warning(f"Scraper returned None for manga id={manga.id} url={manga.url!r}")
                failed += 1
        except Exception as e:
            logger.error(f"Error checking manga id={manga.id} url={manga.url!r}: {e}")
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

    logger.info(f"Recommendations starting — themes: {themes}")
    logger.info(f"Enabled crawler domains: {sorted(enabled_domains)}, min_chapters={min_chapters}, max_pages={max_pages}")

    known_urls = ops.get_all_known_urls()
    excluded_titles = ops.get_all_non_active_titles()
    logger.info(f"Skipping {len(known_urls)} known URLs and {len(excluded_titles)} excluded titles")

    all_available = list(all_crawlers())
    crawlers = [c for c in all_available if c.domain in enabled_domains]
    logger.info(f"Crawlers registered: {[c.domain for c in all_available]} — running {len(crawlers)}: {[c.domain for c in crawlers]}")

    if not crawlers:
        logger.warning("No crawlers match enabled domains — check config.yaml sites[].crawler and domain names")

    added = 0
    seen_titles: set[str] = set()  # deduplicate same title across sites

    for crawler in crawlers:
        logger.info(f"Crawling {crawler.domain} (up to {max_pages} pages)...")
        try:
            candidates = crawler.crawl(
                themes=themes,
                known_urls=known_urls,
                excluded_titles=excluded_titles,
                min_chapters=min_chapters,
                max_pages=max_pages,
            )
            logger.info(f"{crawler.domain}: found {len(candidates)} candidates")
            for c in candidates:
                title_key = c["title"].lower().strip()
                if title_key in seen_titles:
                    logger.debug(f"Skipping duplicate title across sites: {c['title']!r}")
                    continue
                seen_titles.add(title_key)
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
            logger.error(f"Crawler {crawler.domain} failed: {e}", exc_info=True)

    logger.info(f"Recommendations done: {added} candidates added/updated")
    return {"added": added}
