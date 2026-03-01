"""One-time import parser: converts messy Mangas.md → clean DB records.

Run once:
    python import/parse_mangas_md.py

After successful import, Mangas.md is retired and SQLite is the source of truth.
"""
import os
import re
import sys
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

# Allow running from repo root
sys.path.insert(0, str(Path(__file__).parent.parent))

import db.ops as ops

# ---------------------------------------------------------------------------
# Section headings → status
# ---------------------------------------------------------------------------

_SECTION_MAP = {
    "didn't love": "didnt_love",
    "didnt love": "didnt_love",
    "finished": "finished",
    "pass": "pass",
    "pass:": "pass",
}

# ---------------------------------------------------------------------------
# URL extraction helpers
# ---------------------------------------------------------------------------

_URL_PATTERN = re.compile(r"https?://[^\s\])\'\",]+")

# noise words that are never chapter numbers
_NOISE_WORDS = re.compile(
    r"\b(not\s+loading|tv\s+show|season|end|bonus|creators?\s+note|see\s+u)\b",
    re.IGNORECASE,
)


def _extract_urls(line: str) -> list[str]:
    """Find all URLs in a line, cleaning trailing punctuation."""
    raw_urls = _URL_PATTERN.findall(line)
    cleaned = []
    for url in raw_urls:
        # Strip trailing junk that isn't part of the URL
        url = url.rstrip(".,;:)'\"\\#").rstrip()
        # Normalise fragment-only anchors (#)
        if url.endswith("#"):
            url = url[:-1]
        if url:
            cleaned.append(url)
    return cleaned


def _canonical_url(url: str) -> str:
    """Strip chapter paths (e.g. /chapter-85-bonus-episode/) to get the manga root."""
    parsed = urlparse(url)
    path = parsed.path
    # Remove chapter segments from path
    path = re.sub(r"/chapter[^/]*/.*$", "", path, flags=re.IGNORECASE)
    path = re.sub(r"/chapter[^/]*$", "", path, flags=re.IGNORECASE)
    # Ensure trailing slash for consistency
    if path and not path.endswith("/"):
        path += "/"
    return parsed._replace(path=path, fragment="").geturl()


def _extract_numbers(line: str) -> list[int]:
    """Extract all standalone integers from a line, ignoring noise and URL paths."""
    # Remove URLs first (they contain numbers we don't want)
    no_urls = _URL_PATTERN.sub(" ", line)
    # Remove noise
    no_urls = _NOISE_WORDS.sub(" ", no_urls)
    # Find all integers — allow negative sign (e.g. "-72") but only keep positive
    candidates = re.findall(r"-?\d+(?:\.\d+)?", no_urls)
    result = []
    for c in candidates:
        try:
            val = float(c)
            if val > 0 and val == int(val):
                result.append(int(val))
        except ValueError:
            pass
    return result


def _extract_raw_note(line: str) -> Optional[str]:
    """Pull out human annotations like 'not loading', 'tv show'."""
    matches = _NOISE_WORDS.findall(line)
    return " | ".join(m.strip() for m in matches) if matches else None


# ---------------------------------------------------------------------------
# Line parser
# ---------------------------------------------------------------------------


def parse_line(line: str, status: str) -> Optional[dict]:
    """Parse a single Mangas.md line.

    Returns a dict with keys:
        url, status, last_episode_published, last_episode_read, raw_note
    or None if no valid URL found.
    """
    line = line.strip()
    if not line:
        return None

    urls = _extract_urls(line)
    if not urls:
        return None

    # Use first URL as canonical; dedupe in-line duplicates
    canonical = _canonical_url(urls[0])
    if not canonical or not canonical.startswith("http"):
        return None

    numbers = _extract_numbers(line)
    raw_note = _extract_raw_note(line)

    # Determine episode numbers from position
    published: Optional[int] = None
    read: Optional[int] = None

    # Look for bracketed pairs like [257],[255]
    bracket_pairs = re.findall(r"\[(\s*\d+(?:\.\d+)?\s*)\]", line)
    if len(bracket_pairs) >= 2:
        try:
            published = int(float(bracket_pairs[0].strip()))
            read = int(float(bracket_pairs[1].strip()))
        except ValueError:
            pass
    elif len(bracket_pairs) == 1:
        try:
            published = int(float(bracket_pairs[0].strip()))
        except ValueError:
            pass
    elif len(numbers) == 2:
        published, read = numbers[0], numbers[1]
    elif len(numbers) == 1:
        published = numbers[0]
    # No numbers → both remain None

    return {
        "url": canonical,
        "status": status,
        "last_episode_published": published,
        "last_episode_read": read,
        "raw_note": raw_note,
    }


# ---------------------------------------------------------------------------
# Section detection
# ---------------------------------------------------------------------------


def _detect_section(line: str) -> Optional[str]:
    """Return status name if line is a section heading, else None."""
    stripped = line.strip().rstrip(":").lower()
    # Also handle "Didn't love" with smart quotes or apostrophe variants
    stripped = stripped.replace("\u2019", "'").replace("\u2018", "'")
    return _SECTION_MAP.get(stripped)


# ---------------------------------------------------------------------------
# Full file parser
# ---------------------------------------------------------------------------


def parse_mangas_md(filepath: str) -> list[dict]:
    """Parse a Mangas.md file and return a list of record dicts.

    Deduplication: if the same URL appears twice, the record with more data wins.
    """
    current_status = "active"
    records: dict[str, dict] = {}  # url → record

    with open(filepath, encoding="utf-8", errors="replace") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue

            # Check for section heading
            new_status = _detect_section(line)
            if new_status:
                current_status = new_status
                continue

            # Skip header row of any CSV-ish header
            if line.lower().startswith("url,"):
                continue

            record = parse_line(line, current_status)
            if record is None:
                continue

            url = record["url"]
            if url not in records:
                records[url] = record
            else:
                records[url] = _merge(records[url], record)

    return list(records.values())


def _data_score(rec: dict) -> int:
    """Count non-None data fields — used to pick the richer record on merge."""
    score = 0
    for key in ("last_episode_published", "last_episode_read", "raw_note"):
        if rec.get(key) is not None:
            score += 1
    return score


def _merge(existing: dict, incoming: dict) -> dict:
    """Merge two records for the same URL, keeping the richer data."""
    if _data_score(incoming) <= _data_score(existing):
        return existing
    # incoming is richer — but keep non-active status if set
    merged = dict(incoming)
    if existing["status"] != "active":
        merged["status"] = existing["status"]
    return merged


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    import_path = Path(__file__).parent.parent / "data" / "import" / "Mangas.md"
    tmp_path = Path(__file__).parent.parent / "tmp" / "Mangas.md"

    if import_path.exists():
        filepath = str(import_path)
    elif tmp_path.exists():
        filepath = str(tmp_path)
    else:
        print("ERROR: Mangas.md not found. Place it at data/import/Mangas.md")
        sys.exit(1)

    print(f"Parsing {filepath} ...")
    records = parse_mangas_md(filepath)
    print(f"  → {len(records)} unique manga entries found")

    ops.init()

    imported = 0
    skipped = 0
    for rec in records:
        try:
            ops.upsert_manga(
                url=rec["url"],
                status=rec["status"],
                last_episode_published=rec["last_episode_published"],
                last_episode_read=rec["last_episode_read"],
                raw_note=rec["raw_note"],
            )
            imported += 1
        except Exception as e:
            print(f"  SKIP {rec['url']}: {e}")
            skipped += 1

    print(f"Import complete: {imported} imported, {skipped} skipped")
    print("Run 'python import/validate_import.py' to review results.")


if __name__ == "__main__":
    main()
