"""Database layer tests — use in-memory SQLite, no real DB."""
import json

import pytest


def test_upsert_manga_creates(tmp_db):
    import db.ops as ops
    m = ops.upsert_manga(url="https://coffeemanga.io/manga/test/", status="active")
    assert m.id is not None
    assert m.url == "https://coffeemanga.io/manga/test/"


def test_upsert_manga_deduplicates(tmp_db):
    import db.ops as ops
    m1 = ops.upsert_manga(url="https://coffeemanga.io/manga/test/", last_episode_published=50)
    m2 = ops.upsert_manga(url="https://coffeemanga.io/manga/test/", last_episode_published=60)
    assert m1.id == m2.id
    assert m2.last_episode_published == 60


def test_has_update_true(tmp_db):
    import db.ops as ops
    m = ops.upsert_manga(
        url="https://coffeemanga.io/manga/update/",
        last_episode_published=100,
        last_episode_read=90,
    )
    assert m.has_update is True


def test_has_update_false(tmp_db):
    import db.ops as ops
    m = ops.upsert_manga(
        url="https://coffeemanga.io/manga/no-update/",
        last_episode_published=90,
        last_episode_read=90,
    )
    assert m.has_update is False


def test_has_update_no_read(tmp_db):
    """published set but read is None → has_update=True."""
    import db.ops as ops
    m = ops.upsert_manga(
        url="https://coffeemanga.io/manga/unread/",
        last_episode_published=50,
    )
    assert m.has_update is True


def test_mark_chapter_read_updates(tmp_db):
    import db.ops as ops
    m = ops.upsert_manga(
        url="https://coffeemanga.io/manga/read-test/",
        last_episode_published=100,
        last_episode_read=90,
    )
    assert m.has_update is True
    updated = ops.mark_chapter_read(m.id, 100)
    assert updated.last_episode_read == 100
    assert updated.has_update is False


def test_mark_chapter_read_missing_id(tmp_db):
    import db.ops as ops
    result = ops.mark_chapter_read(99999, 10)
    assert result is None


def test_recommendation_not_in_active(tmp_db):
    """URL already in manga table should not be treated as a recommendation."""
    import db.ops as ops
    ops.upsert_manga(url="https://coffeemanga.io/manga/known/", status="active")
    known = ops.get_all_known_urls()
    assert "https://coffeemanga.io/manga/known/" in known


def test_seen_flag_persists(tmp_db):
    import db.ops as ops
    rec = ops.upsert_recommendation(
        url="https://coffeemanga.io/manga/rec/",
        title="Test Rec",
        site="coffeemanga.io",
        chapter_count=150,
        matched_themes=["villainess"],
        score=1,
    )
    assert rec.seen is False
    dismissed = ops.dismiss_recommendation(rec.id)
    assert dismissed.seen is True
    # Should not show up in unseen list
    unseen = ops.get_unseen_recommendations()
    assert all(r.id != rec.id for r in unseen)


def test_json_export_on_write(tmp_db, mocker):
    """Every DB write triggers mangas.json export."""
    import db.ops as ops

    # Patch the reference that db.ops holds directly
    mock_export = mocker.patch("db.ops.export_to_json")

    ops.upsert_manga(url="https://coffeemanga.io/manga/export-test/")
    assert mock_export.call_count >= 1


def test_get_all_active(tmp_db):
    import db.ops as ops
    ops.upsert_manga(url="https://coffeemanga.io/manga/a/", status="active")
    ops.upsert_manga(url="https://coffeemanga.io/manga/b/", status="finished")
    active = ops.get_all_active()
    urls = [m.url for m in active]
    assert "https://coffeemanga.io/manga/a/" in urls
    assert "https://coffeemanga.io/manga/b/" not in urls


def test_get_manga_with_updates(tmp_db):
    import db.ops as ops
    ops.upsert_manga(
        url="https://coffeemanga.io/manga/has-update/",
        last_episode_published=10,
        last_episode_read=5,
    )
    ops.upsert_manga(
        url="https://coffeemanga.io/manga/no-update/",
        last_episode_published=10,
        last_episode_read=10,
    )
    updated = ops.get_manga_with_updates()
    urls = [m.url for m in updated]
    assert "https://coffeemanga.io/manga/has-update/" in urls
    assert "https://coffeemanga.io/manga/no-update/" not in urls


def test_set_bug(tmp_db):
    import db.ops as ops
    m = ops.upsert_manga(url="https://coffeemanga.io/manga/bug-test/", status="active")
    assert m.bug_type is None
    flagged = ops.set_bug(m.id, "wrong_title")
    assert flagged.bug_type == "wrong_title"
    bugs = ops.get_manga_with_bugs()
    assert any(b.id == m.id for b in bugs)


def test_clear_bug(tmp_db):
    import db.ops as ops
    m = ops.upsert_manga(url="https://coffeemanga.io/manga/clear-bug/", status="active")
    ops.set_bug(m.id, "url_broken")
    cleared = ops.clear_bug(m.id)
    assert cleared.bug_type is None
    bugs = ops.get_manga_with_bugs()
    assert all(b.id != m.id for b in bugs)


def test_set_bug_invalid_type(tmp_db):
    import db.ops as ops
    m = ops.upsert_manga(url="https://coffeemanga.io/manga/invalid-bug/", status="active")
    with pytest.raises(ValueError):
        ops.set_bug(m.id, "not_a_valid_type")
