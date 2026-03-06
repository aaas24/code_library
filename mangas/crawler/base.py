"""Abstract base class for recommendation crawlers.

Each crawler browses a site's manga listing pages, filters by theme and
chapter count, and returns candidate recommendations.

Guardrail: max_pages limits the number of listing pages crawled per session
to avoid overwhelming the target site during development.
"""
import urllib.parse
from abc import ABC, abstractmethod
from typing import Optional

import requests
from bs4 import BeautifulSoup

DEFAULT_MAX_PAGES = 5  # Override via config.yaml recommendations.max_pages


class BaseCrawler(ABC):
    """One subclass per supported site. Drop in crawler/ to auto-register."""

    domain: str = ""
    extra_domains: list[str] = []

    _HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }

    def fetch(self, url: str) -> Optional[BeautifulSoup]:
        try:
            resp = requests.get(url, headers=self._HEADERS, timeout=15)
            resp.raise_for_status()
            return BeautifulSoup(resp.text, "lxml")
        except Exception:
            return None

    @abstractmethod
    def listing_url(self, page: int) -> str:
        """Return the URL for page N of the site's manga listing."""

    @abstractmethod
    def parse_listing(self, soup: BeautifulSoup) -> list[dict]:
        """Parse a listing page soup.

        Returns a list of dicts with keys:
            url (str), title (str), chapter_count (int or None)
        """

    def search_url(self, title: str) -> str:
        """Return the search URL for the given title. Override per site."""
        raise NotImplementedError(f"{self.__class__.__name__} does not support search_url")

    def search_by_title(self, title: str) -> list[dict]:
        """Search the site for manga matching title. Returns up to 5 results."""
        url = self.search_url(title)
        soup = self.fetch(url)
        if soup is None:
            return []
        return self.parse_listing(soup)[:5]

    def crawl(
        self,
        themes: list[str],
        known_urls: set[str],
        excluded_titles: set[str],
        min_chapters: int = 100,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[dict]:
        """Crawl up to max_pages listing pages and return filtered candidates.

        Each returned dict has:
            url, title, site, chapter_count, matched_themes, score
        """
        candidates = []
        theme_lower = [t.lower() for t in themes]
        excluded_lower = {t.lower() for t in excluded_titles}

        for page in range(1, max_pages + 1):
            url = self.listing_url(page)
            soup = self.fetch(url)
            if soup is None:
                break

            items = self.parse_listing(soup)
            if not items:
                break  # No more pages

            for item in items:
                item_url = item.get("url", "")
                item_title = (item.get("title") or "").strip()
                chapter_count = item.get("chapter_count") or 0

                # Guardrail filters
                if not item_url or item_url in known_urls:
                    continue
                if item_title.lower() in excluded_lower:
                    continue
                if chapter_count < min_chapters:
                    continue

                # Theme matching — check title and URL slug
                title_lower = item_title.lower()
                slug = item_url.rstrip("/").split("/")[-1].replace("-", " ").replace("_", " ")
                searchable = f"{title_lower} {slug.lower()}"
                matched = [t for t in theme_lower if t in searchable]
                if not matched:
                    continue

                candidates.append(
                    {
                        "url": item_url,
                        "title": item_title,
                        "site": self.domain,
                        "chapter_count": chapter_count,
                        "matched_themes": matched,
                        "score": len(matched),
                    }
                )

        return candidates
