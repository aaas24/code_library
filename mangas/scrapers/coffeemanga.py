"""Scraper for coffeemanga.io / coffeemanga.ink / coffeemanga.moe."""
import re
from typing import Optional

from bs4 import BeautifulSoup

from scrapers.base import BaseScraper


class CoffeeMangaScraper(BaseScraper):
    domain = "coffeemanga.io"
    extra_domains = ["coffeemanga.ink", "coffeemanga.moe"]

    # CSS selectors to try in order
    _SELECTORS = [
        ".wp-manga-chapter:first-child a",
        ".chapter-list li:first-child a",
        ".listing-chapters_wrap li:first-child a",
        "ul.row-content-chapter li:first-child a",
        ".main-col .chapter-item:first-child a",
    ]

    _CHAPTER_RE = re.compile(r"(?:chapter|ch\.?)\s*(\d+(?:\.\d+)?)", re.IGNORECASE)
    _NUMBER_RE = re.compile(r"(\d+(?:\.\d+)?)")

    def get_latest_chapter(self, soup: BeautifulSoup) -> Optional[int]:
        for selector in self._SELECTORS:
            el = soup.select_one(selector)
            if el:
                text = el.get_text(separator=" ", strip=True)
                return self._parse_number(text)
        return None

    def _parse_number(self, text: str) -> Optional[int]:
        m = self._CHAPTER_RE.search(text)
        if m:
            return int(float(m.group(1)))
        m = self._NUMBER_RE.search(text)
        if m:
            return int(float(m.group(1)))
        return None
