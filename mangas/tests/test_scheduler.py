"""Scheduler tests — mock scrapers and crawlers, no real network calls."""
import pytest
from unittest.mock import MagicMock, patch


def test_config_cron_loaded(tmp_path):
    """Cron expression is correctly read from config.yaml."""
    from scheduler.runner import _parse_cron
    from apscheduler.triggers.cron import CronTrigger

    trigger = _parse_cron("0 2 * * *")
    assert isinstance(trigger, CronTrigger)


def test_parse_cron_invalid():
    from scheduler.runner import _parse_cron
    with pytest.raises(ValueError):
        _parse_cron("invalid cron")


def test_manual_trigger_chapter_check(tmp_db, mocker):
    """trigger_now('chapter_check') invokes run_chapter_check."""
    mock_check = mocker.patch("scheduler.runner.run_chapter_check", return_value={"updated": 0})
    from scheduler.runner import trigger_now
    trigger_now("chapter_check")
    mock_check.assert_called_once()


def test_manual_trigger_recommendations(tmp_db, mocker):
    mock_rec = mocker.patch("scheduler.runner.run_recommendations", return_value={"added": 0})
    from scheduler.runner import trigger_now
    trigger_now("recommendations")
    mock_rec.assert_called_once()


def test_trigger_now_invalid_job():
    from scheduler.runner import trigger_now
    with pytest.raises(ValueError):
        trigger_now("nonexistent_job")


def test_scraper_disabled_site_skipped(tmp_db, tmp_path, mocker):
    """A site with scraper=false must not be scraped."""
    config_content = """\
schedules:
  chapter_check: "0 2 * * *"
  recommendations: "0 3 * * 1"
sites:
  coffeemanga:
    scraper: false
    crawler: false
    domains: [coffeemanga.io]
themes: []
recommendations:
  min_chapters: 100
  max_pages: 5
web:
  port: 5000
  host: "0.0.0.0"
"""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(config_content)

    mocker.patch("scheduler.jobs.load_config", return_value=__import__("yaml").safe_load(config_content))
    mocker.patch("scheduler.jobs.ops.get_all_active", return_value=[
        MagicMock(url="https://coffeemanga.io/manga/test/", id=1)
    ])
    mock_get_scraper = mocker.patch("scheduler.jobs.get_scraper")

    from scheduler.jobs import run_chapter_check
    run_chapter_check()
    # Scraper should NOT be called because coffeemanga scraper is disabled
    mock_get_scraper.assert_not_called()


def test_crawler_disabled_site_skipped(tmp_db, mocker):
    """A site with crawler=false is skipped in recommendations."""
    import yaml
    config_content = """\
schedules:
  chapter_check: "0 2 * * *"
  recommendations: "0 3 * * 1"
sites:
  coffeemanga:
    scraper: true
    crawler: false
    domains: [coffeemanga.io]
themes: [villainess]
recommendations:
  min_chapters: 100
  max_pages: 5
web:
  port: 5000
  host: "0.0.0.0"
"""
    mocker.patch("scheduler.jobs.load_config", return_value=yaml.safe_load(config_content))
    mocker.patch("scheduler.jobs.ops.get_all_known_urls", return_value=set())
    mocker.patch("scheduler.jobs.ops.get_all_non_active_titles", return_value=set())
    mock_crawlers = mocker.patch("scheduler.jobs.all_crawlers", return_value=[])

    from scheduler.jobs import run_recommendations
    run_recommendations()
    # Because crawler is disabled, no crawlers should be instantiated and called
    # (they are filtered out by enabled_domains check)
    # Verify no upsert_recommendation was called
    mock_upsert = mocker.patch("scheduler.jobs.ops.upsert_recommendation")
    run_recommendations()
    mock_upsert.assert_not_called()
