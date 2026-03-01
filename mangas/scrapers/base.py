"""Abstract base class for chapter scrapers."""
from abc import ABC, abstractmethod
from typing import Optional

import requests
from bs4 import BeautifulSoup


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
        except Exception:
            return None

    @abstractmethod
    def get_latest_chapter(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract the latest chapter number from a manga page's soup.

        Returns None if not found or on any parsing error.
        """

    def check(self, url: str) -> Optional[int]:
        """Fetch the URL and return the latest chapter number."""
        soup = self.fetch(url)
        if soup is None:
            return None
        return self.get_latest_chapter(soup)

    @classmethod
    def handles(cls, domain: str) -> bool:
        all_domains = [cls.domain] + list(cls.extra_domains)
        return domain in all_domains
