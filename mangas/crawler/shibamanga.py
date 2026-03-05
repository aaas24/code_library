"""Recommendation crawler for shibamanga.com."""
import re

from bs4 import BeautifulSoup

from crawler.base import BaseCrawler


class ShibaMangaCrawler(BaseCrawler):
    domain = "shibamanga.com"

    _BASE = "https://shibamanga.com"
    _CHAPTER_RE = re.compile(r"[Cc]hapter\s+(\d+)")

    def listing_url(self, page: int) -> str:
        return f"{self._BASE}/manga/?page={page}&order=views"

    def parse_listing(self, soup: BeautifulSoup) -> list[dict]:
        results = []
        for card in soup.select(".page-item-detail"):
            link_el = card.select_one(".post-title a[href], h3 a[href], h4 a[href]")
            if not link_el:
                continue

            url = link_el.get("href", "").strip()
            title = link_el.get("title") or link_el.get_text(strip=True)
            chapter_count = self._extract_chapter_count(card)

            if url:
                results.append({"url": url, "title": title, "chapter_count": chapter_count})
        return results

    def _extract_chapter_count(self, card) -> int:
        nums = [int(m.group(1)) for m in self._CHAPTER_RE.finditer(card.get_text(separator=" "))]
        return max(nums) if nums else 0
