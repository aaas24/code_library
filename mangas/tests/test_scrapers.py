"""Scraper tests — use fixture HTML, no real network calls."""
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def _soup(filename: str) -> BeautifulSoup:
    html = (FIXTURE_DIR / filename).read_text(encoding="utf-8")
    return BeautifulSoup(html, "lxml")


# ---------------------------------------------------------------------------
# Chapter extraction from fixture HTML
# ---------------------------------------------------------------------------


def test_coffeemanga_chapter_extraction():
    from scrapers.coffeemanga import CoffeeMangaScraper
    scraper = CoffeeMangaScraper()
    soup = _soup("coffeemanga_chapter.html")
    chapter = scraper.get_latest_chapter(soup)
    assert chapter == 157


def test_shibamanga_chapter_extraction():
    from scrapers.shibamanga import ShibaMangaScraper
    scraper = ShibaMangaScraper()
    soup = _soup("shibamanga_chapter.html")
    chapter = scraper.get_latest_chapter(soup)
    assert chapter == 89


def test_kaliscan_chapter_extraction():
    from scrapers.kaliscan import KaliScanScraper
    scraper = KaliScanScraper()
    soup = _soup("kaliscan_chapter.html")
    chapter = scraper.get_latest_chapter(soup)
    assert chapter == 219


def test_manhuascan_chapter_extraction():
    from scrapers.manhuascan import ManhuaScanScraper
    scraper = ManhuaScanScraper()
    soup = _soup("manhuascan_chapter.html")
    chapter = scraper.get_latest_chapter(soup)
    assert chapter == 115


def test_scraper_returns_none_missing_element():
    """Empty HTML → returns None gracefully."""
    from scrapers.coffeemanga import CoffeeMangaScraper
    scraper = CoffeeMangaScraper()
    soup = BeautifulSoup("<html><body><p>No chapters here</p></body></html>", "lxml")
    assert scraper.get_latest_chapter(soup) is None


def test_scraper_returns_none_on_404(mocker):
    """HTTP error → check() returns None."""
    from scrapers.coffeemanga import CoffeeMangaScraper
    scraper = CoffeeMangaScraper()
    mocker.patch.object(scraper, "fetch", return_value=None)
    assert scraper.check("https://coffeemanga.io/manga/test/") is None


# ---------------------------------------------------------------------------
# Registry tests
# ---------------------------------------------------------------------------


def test_registry_autodiscovers_scrapers():
    from scrapers.registry import registered_domains, _discover
    from scrapers import registry
    registry._discovered = False  # force re-discovery
    registry._REGISTRY.clear()
    domains = registered_domains()
    assert "coffeemanga.io" in domains
    assert "shibamanga.com" in domains
    assert "kaliscan.io" in domains
    assert "manhuascan.com" in domains


def test_registry_returns_correct_scraper():
    from scrapers.registry import get_scraper
    from scrapers.coffeemanga import CoffeeMangaScraper
    scraper = get_scraper("coffeemanga.io")
    assert isinstance(scraper, CoffeeMangaScraper)


def test_extra_domains_resolved():
    """coffeemanga.ink and coffeemanga.moe should map to CoffeeMangaScraper."""
    from scrapers.registry import get_scraper
    from scrapers.coffeemanga import CoffeeMangaScraper
    for domain in ["coffeemanga.ink", "coffeemanga.moe"]:
        scraper = get_scraper(domain)
        assert isinstance(scraper, CoffeeMangaScraper), f"Failed for {domain}"
