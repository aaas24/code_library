"""Web route tests — use Flask test client, no real network calls."""
import pytest


def test_root_redirects_to_active(client):
    resp = client.get("/")
    assert resp.status_code == 302
    assert "/active" in resp.headers["Location"]


def test_home_200(client):
    resp = client.get("/home")
    assert resp.status_code == 200
    assert b"Manga Tracker" in resp.data


def test_updates_200(client):
    resp = client.get("/updates")
    assert resp.status_code == 200


def test_updates_shows_only_updated(client, tmp_db):
    """Only manga with has_update=True should appear on /updates."""
    import db.ops as ops
    ops.upsert_manga(
        url="https://coffeemanga.io/manga/has-update/",
        title="Has Update",
        last_episode_published=10,
        last_episode_read=5,
    )
    ops.upsert_manga(
        url="https://coffeemanga.io/manga/no-update/",
        title="No Update",
        last_episode_published=5,
        last_episode_read=5,
    )
    resp = client.get("/updates")
    assert b"Has Update" in resp.data
    assert b"No Update" not in resp.data


def test_active_shows_all_active(client, tmp_db):
    import db.ops as ops
    ops.upsert_manga(url="https://coffeemanga.io/manga/a/", title="Manga A", status="active")
    ops.upsert_manga(url="https://coffeemanga.io/manga/b/", title="Manga B", status="finished")
    resp = client.get("/active")
    assert b"Manga A" in resp.data
    assert b"Manga B" not in resp.data


def test_recommendations_shows_unseen(client, tmp_db):
    import db.ops as ops
    ops.upsert_recommendation(
        url="https://coffeemanga.io/manga/rec-a/",
        title="Rec A",
        site="coffeemanga.io",
        chapter_count=150,
        matched_themes=["villainess"],
        score=1,
    )
    seen_rec = ops.upsert_recommendation(
        url="https://coffeemanga.io/manga/rec-b/",
        title="Rec B",
        site="coffeemanga.io",
        chapter_count=200,
        matched_themes=["empress"],
        score=1,
    )
    ops.dismiss_recommendation(seen_rec.id)

    resp = client.get("/recommendations")
    assert b"Rec A" in resp.data
    assert b"Rec B" not in resp.data


def test_dismiss_recommendation(client, tmp_db):
    import db.ops as ops
    rec = ops.upsert_recommendation(
        url="https://coffeemanga.io/manga/dismiss-me/",
        title="Dismiss Me",
        site="coffeemanga.io",
        chapter_count=120,
        matched_themes=["noble"],
        score=1,
    )
    resp = client.post(f"/recommendations/{rec.id}/ignore", follow_redirects=True)
    assert resp.status_code == 200
    updated = ops.dismiss_recommendation.__wrapped__ if hasattr(ops.dismiss_recommendation, "__wrapped__") else None
    # Verify directly
    unseen = ops.get_unseen_recommendations()
    assert all(r.id != rec.id for r in unseen)


def test_read_redirect(client, tmp_db):
    import db.ops as ops
    m = ops.upsert_manga(
        url="https://coffeemanga.io/manga/redirect-test/",
        last_episode_published=100,
        last_episode_read=90,
    )
    resp = client.get(f"/read/{m.id}/100")
    assert resp.status_code == 302
    assert "coffeemanga.io" in resp.headers["Location"]
    # Verify DB updated
    updated = ops.get_manga_by_id(m.id)
    assert updated.last_episode_read == 100


def test_read_unknown_manga_404(client, tmp_db):
    resp = client.get("/read/99999/100")
    assert resp.status_code == 404


def test_settings_200(client):
    resp = client.get("/settings")
    assert resp.status_code == 200
    assert b"Schedules" in resp.data


def test_run_now_triggers_crawl(client, mocker):
    # trigger_now is imported inside the route function, so patch at the source
    mock_trigger = mocker.patch("scheduler.runner.trigger_now")
    resp = client.post(
        "/settings/run-now",
        data={"job": "chapter_check"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    mock_trigger.assert_called_once_with("chapter_check")
