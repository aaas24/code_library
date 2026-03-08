"""URL and title canonicalization helpers for manga records."""
import re
from urllib.parse import urlparse

# Strips /chapter-N/ or /chapter-85-bonus-episode/ from paths
_CHAPTER_PATH_RE = re.compile(r"/chapter[^/]*/.*$|/chapter[^/]*$", re.IGNORECASE)

# Strips " - Chapter N..." and everything that follows (e.g. "- Chapter 12 - Coffee Manga")
_CHAPTER_TITLE_RE = re.compile(r"\s*-\s*chapter\s*\d+.*$", re.IGNORECASE)


def canonical_manga_url(url: str) -> str:
    """Strip chapter paths from a manga URL to get the manga root URL.

    Example:
        https://coffeemanga.ink/manga/one-night-besides-the-dragon/chapter-12/
        → https://coffeemanga.ink/manga/one-night-besides-the-dragon/
    """
    parsed = urlparse(url)
    path = _CHAPTER_PATH_RE.sub("", parsed.path)
    if path and not path.endswith("/"):
        path += "/"
    return parsed._replace(path=path, fragment="").geturl()


def clean_page_title(title: str) -> str:
    """Strip chapter number and trailing site-name suffix from a page title.

    Example:
        "One Night Besides the Dragon - Chapter 12 - Coffee Manga"
        → "One Night Besides the Dragon"
    """
    return _CHAPTER_TITLE_RE.sub("", title).strip()
