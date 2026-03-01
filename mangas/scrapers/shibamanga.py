"""Scraper for shibamanga.com."""
import re
from typing import Optional

from bs4 import BeautifulSoup

from scrapers.base import BaseScraper


class ShibaMangaScraper(BaseScraper):
    domain = "shibamanga.com"

    _SELECTORS = [
        ".chapter-list li:first-child a",
        ".chapters li:first-child a",
        ".wp-manga-chapter:first-child a",
        "#chapterlist li:first-child a",
        ".listing-chapters_wrap li:first-child a",
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
