"""Abstract base class for chapter scrapers."""
import logging
from abc import ABC, abstractmethod
from typing import Optional

import requests
from bs4 import BeautifulSoup

from utils.manga_url import canonical_manga_url

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """One subclass per supported site. Drop in scrapers/ to auto-register."""

    # Override in subclass with the primary domain, e.g. "coffeemanga.io"
    domain: str = ""

    # Additional domains served by the same scraper (optional)
    extra_domains: list[str] = []

    _HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }

    def fetch(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch a URL and return a BeautifulSoup object, or None on error."""
        try:
            resp = requests.get(url, headers=self._HEADERS, timeout=15)
            resp.raise_for_status()
            return BeautifulSoup(resp.text, "lxml")
        except Exception as e:
            logger.warning(f"[{self.domain}] fetch failed for {url!r}: {e}")
            return None

    @abstractmethod
    def get_latest_chapter(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract the latest chapter number from a manga page's soup.

        Returns None if not found or on any parsing error.
        """

    def check(self, url: str) -> Optional[int]:
        """Fetch the URL and return the latest chapter number."""
        canonical = canonical_manga_url(url)
        if canonical != url:
            logger.info(f"[{self.domain}] canonicalized URL {url!r} -> {canonical!r}")
        soup = self.fetch(canonical)
        if soup is None:
            logger.warning(f"[{self.domain}] fetch returned None for {canonical!r}")
            return None
        chapter = self.get_latest_chapter(soup)
        if chapter is None:
            logger.warning(f"[{self.domain}] no chapter found in page {canonical!r} — selector may not match")
        return chapter

    def clean_title(self, title: str) -> str:
        """Override in subclasses to normalize site-specific title quirks."""
        return title

    @classmethod
    def handles(cls, domain: str) -> bool:
        all_domains = [cls.domain] + list(cls.extra_domains)
        return domain in all_domains
