"""Recommendation crawler for kaliscan.io."""
import re
import urllib.parse

from bs4 import BeautifulSoup

from crawler.base import BaseCrawler


class KaliScanCrawler(BaseCrawler):
    domain = "kaliscan.io"

    _BASE = "https://kaliscan.io"
    _CHAPTER_RE = re.compile(r"[Cc]hapter\s+(\d+)")
    _TITLE_ID_RE = re.compile(r"^\d+\s+")

    def listing_url(self, page: int) -> str:
        return f"{self._BASE}/popular?page={page}"

    def search_url(self, title: str) -> str:
        return f"{self._BASE}/search?q={urllib.parse.quote_plus(title)}"

    def parse_listing(self, soup: BeautifulSoup) -> list[dict]:
        results = []
        for card in soup.select(".book-detailed-item"):
            link_el = card.select_one(".title a[href], h3 a[href]")
            if not link_el:
                continue

            url = self._BASE + link_el.get("href", "").strip()
            raw_title = link_el.get("title") or link_el.get_text(strip=True)
            title = self._TITLE_ID_RE.sub("", raw_title).strip()
            chapter_count = self._extract_chapter_count(card)

            if url:
                results.append({"url": url, "title": title, "chapter_count": chapter_count})
        return results

    def _extract_chapter_count(self, card) -> int:
        el = card.select_one(".latest-chapter")
        if el:
            m = self._CHAPTER_RE.search(el.get_text())
            if m:
                return int(m.group(1))
        return 0
