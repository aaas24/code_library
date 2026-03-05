"""Scraper for shibamanga.com.

Chapter list is not in the initial page HTML — it is fetched via a POST
request to {manga_url}ajax/chapters/ with X-Requested-With: XMLHttpRequest.
"""
import re
from typing import Optional

import requests
from bs4 import BeautifulSoup

from scrapers.base import BaseScraper


class ShibaMangaScraper(BaseScraper):
    domain = "shibamanga.com"

    _CHAPTER_RE = re.compile(r"(?:chapter|ch\.?)\s*(\d+(?:\.\d+)?)", re.IGNORECASE)
    _NUMBER_RE = re.compile(r"(\d+(?:\.\d+)?)")

    def check(self, url: str) -> Optional[int]:
        """Fetch the AJAX chapter list and return the highest chapter number."""
        ajax_url = url.rstrip("/") + "/ajax/chapters/"
        headers = {**self._HEADERS, "X-Requested-With": "XMLHttpRequest", "Referer": url}
        try:
            resp = requests.post(ajax_url, headers=headers, timeout=15)
            resp.raise_for_status()
        except Exception:
            return None
        return self.get_latest_chapter(BeautifulSoup(resp.text, "lxml"))

    def get_latest_chapter(self, soup: BeautifulSoup) -> Optional[int]:
        el = soup.select_one(".wp-manga-chapter:first-child a")
        if el:
            return self._parse_number(el.get_text(separator=" ", strip=True))
        return None

    def _parse_number(self, text: str) -> Optional[int]:
        m = self._CHAPTER_RE.search(text)
        if m:
            return int(float(m.group(1)))
        m = self._NUMBER_RE.search(text)
        if m:
            return int(float(m.group(1)))
        return None
