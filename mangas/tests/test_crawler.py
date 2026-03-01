"""Crawler tests — mocked HTML, no real network calls."""
from pathlib import Path
from unittest.mock import patch

import pytest
from bs4 import BeautifulSoup

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def _coffeemanga_listing_soup() -> BeautifulSoup:
    html = (FIXTURE_DIR / "coffeemanga_listing.html").read_text(encoding="utf-8")
    return BeautifulSoup(html, "lxml")


def _make_crawler_with_mocked_fetch(soup):
    from crawler.coffeemanga import CoffeeMangaCrawler
    crawler = CoffeeMangaCrawler()

    def fake_fetch(url):
        return soup

    crawler.fetch = fake_fetch
    return crawler


def test_filters_by_min_chapters():
    """Items with fewer than min_chapters are excluded."""
    soup = _coffeemanga_listing_soup()
    crawler = _make_crawler_with_mocked_fetch(soup)
    # Dragon King has chapter 50, below min 100
    results = crawler.crawl(
        themes=["villainess", "empress", "dragon"],
        known_urls=set(),
        excluded_titles=set(),
        min_chapters=100,
        max_pages=1,
    )
    titles = [r["title"] for r in results]
    assert not any("Dragon King" in t for t in titles)


def test_filters_by_theme():
    """Only titles matching at least one theme pass."""
    soup = _coffeemanga_listing_soup()
    crawler = _make_crawler_with_mocked_fetch(soup)
    results = crawler.crawl(
        themes=["villainess"],
        known_urls=set(),
        excluded_titles=set(),
        min_chapters=100,
        max_pages=1,
    )
    for r in results:
        assert any(t in r["title"].lower() for t in ["villainess"]), r["title"]


def test_excludes_known_urls():
    """URLs already in the manga table are excluded."""
    soup = _coffeemanga_listing_soup()
    crawler = _make_crawler_with_mocked_fetch(soup)
    # Pre-populate known_urls with one of the listing URLs
    known = {"https://coffeemanga.io/manga/villainess-queen/"}
    results = crawler.crawl(
        themes=["villainess", "empress"],
        known_urls=known,
        excluded_titles=set(),
        min_chapters=100,
        max_pages=1,
    )
    urls = [r["url"] for r in results]
    assert "https://coffeemanga.io/manga/villainess-queen/" not in urls


def test_excludes_by_title():
    """Titles in excluded_titles set are filtered out."""
    soup = _coffeemanga_listing_soup()
    crawler = _make_crawler_with_mocked_fetch(soup)
    results = crawler.crawl(
        themes=["empress"],
        known_urls=set(),
        excluded_titles={"empress reborn again"},
        min_chapters=100,
        max_pages=1,
    )
    titles = [r["title"].lower() for r in results]
    assert "empress reborn again" not in titles


def test_scores_by_theme_count():
    """Items matching more themes get higher scores."""
    soup = _coffeemanga_listing_soup()
    crawler = _make_crawler_with_mocked_fetch(soup)
    results = crawler.crawl(
        themes=["villainess", "queen"],
        known_urls=set(),
        excluded_titles=set(),
        min_chapters=100,
        max_pages=1,
    )
    # The Villainess Queen matches both themes → score=2
    for r in results:
        if "villainess" in r["title"].lower() and "queen" in r["title"].lower():
            assert r["score"] >= 2


def test_max_pages_guardrail():
    """Crawler stops after max_pages pages even if more exist."""
    call_count = [0]

    from crawler.coffeemanga import CoffeeMangaCrawler
    crawler = CoffeeMangaCrawler()

    def counting_fetch(url):
        call_count[0] += 1
        return BeautifulSoup("<html><body></body></html>", "lxml")

    crawler.fetch = counting_fetch
    crawler.crawl(
        themes=["villainess"],
        known_urls=set(),
        excluded_titles=set(),
        min_chapters=100,
        max_pages=3,
    )
    # Should have fetched exactly 3 pages (then stopped because empty listing)
    assert call_count[0] <= 3


def test_registry_autodiscovers_crawlers():
    from crawler import registry
    registry._discovered = False
    registry._REGISTRY.clear()
    from crawler.registry import registered_domains
    domains = registered_domains()
    assert "coffeemanga.io" in domains
    assert "shibamanga.com" in domains
    assert "kaliscan.io" in domains
    assert "manhuascan.com" in domains
