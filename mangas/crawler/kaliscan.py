"""Recommendation crawler for kaliscan.io."""
import re

from bs4 import BeautifulSoup

from crawler.base import BaseCrawler


class KaliScanCrawler(BaseCrawler):
    domain = "kaliscan.io"

    _BASE = "https://kaliscan.io"
    _CHAPTER_RE = re.compile(r"(\d+(?:\.\d+)?)")

    def listing_url(self, page: int) -> str:
        return f"{self._BASE}/manga/?page={page}&order=views"

    def parse_listing(self, soup: BeautifulSoup) -> list[dict]:
        results = []
        for card in soup.select(".manga-item, .page-item-detail, .item, .c-image-hover"):
            link_el = card.select_one("a[href]")
            title_el = card.select_one(".manga-name, .post-title, h3 a, h4 a")

            if not link_el:
                continue

            url = link_el.get("href", "").strip()
            title = (title_el or link_el).get_text(strip=True)
            chapter_count = self._extract_chapter_count(card)

            if url:
                results.append({"url": url, "title": title, "chapter_count": chapter_count})
        return results

    def _extract_chapter_count(self, card) -> int:
        text = card.get_text(separator=" ", strip=True)
        m = self._CHAPTER_RE.search(text)
        return int(float(m.group(1))) if m else 0
