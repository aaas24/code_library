"""Tests for import/parse_mangas_md.py — no network calls.

The `import/` folder name is a Python reserved word, so we load it via importlib.
"""
import importlib.util
import textwrap
from pathlib import Path

import pytest

# Load parse_mangas_md from the import/ folder (can't use regular import syntax)
_MODULE_PATH = Path(__file__).parent.parent / "import" / "parse_mangas_md.py"
_spec = importlib.util.spec_from_file_location("parse_mangas_md", _MODULE_PATH)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

parse_line = _mod.parse_line
parse_mangas_md = _mod.parse_mangas_md
_canonical_url = _mod._canonical_url


# ---------------------------------------------------------------------------
# parse_line tests
# ---------------------------------------------------------------------------


def test_parse_bare_url():
    result = parse_line("https://coffeemanga.io/manga/some-manga/", "active")
    assert result is not None
    assert result["url"].startswith("https://coffeemanga.io")
    assert result["status"] == "active"
    assert result["last_episode_published"] is None
    assert result["last_episode_read"] is None


def test_parse_url_one_number():
    result = parse_line(
        "[https://coffeemanga.io/manga/test/](https://coffeemanga.io/manga/test/) 130",
        "active",
    )
    assert result is not None
    assert result["last_episode_published"] == 130
    assert result["last_episode_read"] is None


def test_parse_url_two_numbers():
    result = parse_line(
        "https://shibamanga.com/manga/test/ 99 100",
        "active",
    )
    assert result is not None
    assert result["last_episode_published"] == 99
    assert result["last_episode_read"] == 100


def test_parse_markdown_link():
    result = parse_line(
        "[The Great Manga](https://kaliscan.io/manga/12345-great/) 130",
        "active",
    )
    assert result is not None
    assert "kaliscan.io" in result["url"]
    assert result["last_episode_published"] == 130


def test_parse_bracketed_numbers():
    result = parse_line(
        "['https://mangakomi.io/manga/akatsuki/'],[257],[255]",
        "active",
    )
    assert result is not None
    assert result["last_episode_published"] == 257
    assert result["last_episode_read"] == 255


def test_noise_stripped():
    result = parse_line(
        "['https://shibamanga.com/manga/magic-emperor/'],751 - not loading. Look loaded 769",
        "active",
    )
    assert result is not None
    # raw_note should capture the noise
    assert result["raw_note"] is not None
    # Numbers from noise context are unreliable — just check URL parsed
    assert "shibamanga.com" in result["url"]


def test_section_active():
    """Lines before any heading → active."""
    result = parse_line("https://coffeemanga.io/manga/test/", "active")
    assert result["status"] == "active"


def test_section_didnt_love():
    result = parse_line("https://coffeemanga.io/manga/test/", "didnt_love")
    assert result["status"] == "didnt_love"


def test_section_finished():
    result = parse_line("https://coffeemanga.io/manga/test/", "finished")
    assert result["status"] == "finished"


def test_section_pass():
    result = parse_line("https://coffeemanga.io/manga/test/", "pass")
    assert result["status"] == "pass"


def test_malformed_lines_skipped():
    """Lines with no URL are silently skipped."""
    result = parse_line("url,last_episode_published,last_episode_read", "active")
    assert result is None

    result = parse_line("", "active")
    assert result is None

    result = parse_line("Just some random text with no URL", "active")
    assert result is None


# ---------------------------------------------------------------------------
# Full file parse tests
# ---------------------------------------------------------------------------


def test_deduplication(tmp_path):
    content = textwrap.dedent(
        """\
        https://coffeemanga.io/manga/dupe/ 50
        https://coffeemanga.io/manga/dupe/ 75 60
        """
    )
    md_file = tmp_path / "Mangas.md"
    md_file.write_text(content)
    records = parse_mangas_md(str(md_file))
    urls = [r["url"] for r in records]
    # Deduplicated: only one entry per URL
    assert len(urls) == 1
    # The richer record (two numbers) wins
    rec = records[0]
    assert rec["last_episode_published"] == 75
    assert rec["last_episode_read"] == 60


def test_section_detection_full_file(tmp_path):
    content = textwrap.dedent(
        """\
        https://coffeemanga.io/manga/active-manga/ 10

        Didn't love

        https://coffeemanga.io/manga/didnt-love-manga/ 5

        Finished

        https://coffeemanga.io/manga/finished-manga/

        Pass:

        https://coffeemanga.io/manga/pass-manga/
        """
    )
    md_file = tmp_path / "Mangas.md"
    md_file.write_text(content)
    records = parse_mangas_md(str(md_file))
    by_url = {r["url"]: r for r in records}

    assert any(r["status"] == "active" for r in records)
    assert any(r["status"] == "didnt_love" for r in records)
    assert any(r["status"] == "finished" for r in records)
    assert any(r["status"] == "pass" for r in records)


# ---------------------------------------------------------------------------
# _canonical_url tests
# ---------------------------------------------------------------------------


def test_canonical_url_strips_chapter_path():
    url = "https://coffeemanga.io/manga/evangelines-sword-online/chapter-85-bonus-episode/"
    canonical = _canonical_url(url)
    assert "chapter" not in canonical.lower()
    assert "evangelines-sword-online" in canonical


def test_canonical_url_bare():
    url = "https://coffeemanga.io/manga/test-manga/"
    assert _canonical_url(url) == url
