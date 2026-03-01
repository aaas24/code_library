"""Recommendation crawler for coffeemanga.io."""
import re
from typing import Optional

from bs4 import BeautifulSoup

from crawler.base import BaseCrawler


class CoffeeMangaCrawler(BaseCrawler):
    domain = "coffeemanga.io"
    extra_domains = ["coffeemanga.ink", "coffeemanga.moe"]

    _BASE = "https://coffeemanga.io"
    _CHAPTER_RE = re.compile(r"(\d+(?:\.\d+)?)")

    def listing_url(self, page: int) -> str:
        return f"{self._BASE}/manga/?page={page}&order=views"

    def parse_listing(self, soup: BeautifulSoup) -> list[dict]:
        results = []
        # Try multiple layout patterns
        for card in soup.select(".manga-item, .page-item-detail, .c-image-hover"):
            link_el = card.select_one("a[href]")
            title_el = card.select_one(".manga-name, .post-title, h3 a, h4 a, .item-summary a")

            if not link_el:
                continue

            url = link_el.get("href", "").strip()
            title = (title_el or link_el).get_text(strip=True) if (title_el or link_el) else ""

            # Chapter count — look for "Chapter NNN" text in card
            chapter_count = self._extract_chapter_count(card)
            if url:
                results.append({"url": url, "title": title, "chapter_count": chapter_count})
        return results

    def _extract_chapter_count(self, card) -> int:
        text = card.get_text(separator=" ", strip=True)
        m = self._CHAPTER_RE.search(text)
        if m:
            return int(float(m.group(1)))
        return 0
