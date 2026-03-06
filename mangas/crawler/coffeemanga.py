"""Recommendation crawler for coffeemanga.io."""
import re
import urllib.parse

from bs4 import BeautifulSoup

from crawler.base import BaseCrawler


class CoffeeMangaCrawler(BaseCrawler):
    domain = "coffeemanga.io"
    extra_domains = ["coffeemanga.ink", "coffeemanga.moe"]

    _BASE = "https://coffeemanga.io"
    _CHAPTER_RE = re.compile(r"[Cc]hapter\s+(\d+)")

    def listing_url(self, page: int) -> str:
        return f"{self._BASE}/manga/?page={page}&order=views"

    def search_url(self, title: str) -> str:
        return f"{self._BASE}/?s={urllib.parse.quote_plus(title)}"

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
        """Return the highest chapter number found in the card (latest chapter = proxy for total)."""
        nums = [int(m.group(1)) for m in self._CHAPTER_RE.finditer(card.get_text(separator=" "))]
        return max(nums) if nums else 0
