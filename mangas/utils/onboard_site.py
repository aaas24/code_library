"""Helper: auto-detects CSS selectors for a new manga site.

Usage:
    python utils/onboard_site.py --url "https://newsite.com/manga/some-title"
    python utils/onboard_site.py --test "https://newsite.com/manga/some-title"
"""
import argparse
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

import requests
import yaml
from bs4 import BeautifulSoup

CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"

# Candidate CSS selectors to try, in priority order
CANDIDATE_SELECTORS = [
    ".chapter-list li:first-child",
    ".chapters li:first-child",
    ".chapter-item:first-child",
    ".wp-manga-chapter:first-child",
    "ul.row-content-chapter li:first-child a",
    ".listing-chapters_wrap li:first-child a",
    "#chapterlist li:first-child a",
    ".chapter a:first-child",
    "[class*='chapter']:first-child",
]

# Pattern to pull a number from text
_CHAPTER_RE = re.compile(r"(?:chapter|ch\.?)\s*(\d+(?:\.\d+)?)", re.IGNORECASE)
_ANY_NUMBER_RE = re.compile(r"\b(\d+(?:\.\d+)?)\b")


def fetch_page(url: str) -> BeautifulSoup:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "lxml")


def _extract_number_from_text(text: str):
    m = _CHAPTER_RE.search(text)
    if m:
        return m.group(1)
    m = _ANY_NUMBER_RE.search(text)
    return m.group(1) if m else None


def auto_detect_selector(soup: BeautifulSoup) -> tuple[str | None, str | None]:
    """Try known selectors and return (selector, chapter_number) for the first match."""
    for selector in CANDIDATE_SELECTORS:
        try:
            el = soup.select_one(selector)
            if el:
                text = el.get_text(separator=" ", strip=True)
                number = _extract_number_from_text(text)
                if number:
                    return selector, number
        except Exception:
            continue
    return None, None


def _domain_from_url(url: str) -> str:
    return urlparse(url).netloc.lstrip("www.")


def _load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _save_config(config: dict) -> None:
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)


def _write_site_config(domain: str, selector: str) -> None:
    config = _load_config()
    site_key = domain.split(".")[0]
    if "sites" not in config:
        config["sites"] = {}
    if site_key not in config["sites"]:
        config["sites"][site_key] = {"scraper": True, "crawler": False, "domains": [domain]}
    config["sites"][site_key]["selector"] = selector
    if domain not in config["sites"][site_key].get("domains", []):
        config["sites"][site_key].setdefault("domains", []).append(domain)
    _save_config(config)
    print(f"✓ Wrote selector for '{site_key}' to config.yaml")


def cmd_onboard(url: str) -> None:
    domain = _domain_from_url(url)
    print(f"Fetching {url} ...")
    soup = fetch_page(url)

    selector, chapter = auto_detect_selector(soup)

    if selector and chapter:
        print(f"\nFound: Chapter {chapter} using selector: {selector}")
        answer = input("Correct? (y/n): ").strip().lower()
        if answer == "y":
            _write_site_config(domain, selector)
            return

    # Manual fallback
    print("\nAuto-detect failed. Inspect the HTML and enter the CSS selector manually.")
    selector = input("CSS selector: ").strip()
    if not selector:
        print("No selector entered. Aborting.")
        sys.exit(1)

    el = soup.select_one(selector)
    if el:
        text = el.get_text(separator=" ", strip=True)
        print(f"Element found. Text: {text!r}")
        chapter = _extract_number_from_text(text)
        print(f"Extracted chapter: {chapter}")
        confirm = input("Write to config? (y/n): ").strip().lower()
        if confirm == "y":
            _write_site_config(domain, selector)
    else:
        print("No element found for that selector. Check the HTML and try again.")


def cmd_test(url: str) -> None:
    domain = _domain_from_url(url)
    config = _load_config()
    site_key = domain.split(".")[0]
    site_cfg = config.get("sites", {}).get(site_key, {})
    selector = site_cfg.get("selector")

    if not selector:
        print(f"No selector configured for '{site_key}'. Run without --test first.")
        sys.exit(1)

    print(f"Testing selector '{selector}' on {url} ...")
    soup = fetch_page(url)
    el = soup.select_one(selector)
    if el:
        text = el.get_text(separator=" ", strip=True)
        chapter = _extract_number_from_text(text)
        print(f"✓ Element found. Text: {text!r}")
        print(f"  Extracted chapter: {chapter}")
    else:
        print(f"✗ No element matched selector '{selector}'")


def main():
    parser = argparse.ArgumentParser(description="Onboard a new manga site")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", help="URL of a manga page to onboard")
    group.add_argument("--test", help="URL to test the existing saved selector")
    args = parser.parse_args()

    if args.url:
        cmd_onboard(args.url)
    else:
        cmd_test(args.test)


if __name__ == "__main__":
    main()
