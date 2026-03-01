"""APScheduler setup — reads cron config from config.yaml and runs jobs."""
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from scheduler.jobs import run_chapter_check, run_recommendations
from utils.config_loader import load_config, reload_config

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def _parse_cron(cron_expr: str) -> CronTrigger:
    """Parse a '0 2 * * *' style cron expression into a CronTrigger."""
    parts = cron_expr.strip().split()
    if len(parts) != 5:
        raise ValueError(f"Invalid cron expression: {cron_expr!r}")
    minute, hour, day, month, day_of_week = parts
    return CronTrigger(
        minute=minute,
        hour=hour,
        day=day,
        month=month,
        day_of_week=day_of_week,
    )


def start_scheduler() -> BackgroundScheduler:
    """Create and start the background scheduler. Returns the scheduler."""
    global _scheduler
    config = load_config()
    schedules = config.get("schedules", {})

    _scheduler = BackgroundScheduler()

    chapter_cron = schedules.get("chapter_check", "0 2 * * *")
    rec_cron = schedules.get("recommendations", "0 3 * * 1")

    _scheduler.add_job(
        run_chapter_check,
        trigger=_parse_cron(chapter_cron),
        id="chapter_check",
        replace_existing=True,
    )
    _scheduler.add_job(
        run_recommendations,
        trigger=_parse_cron(rec_cron),
        id="recommendations",
        replace_existing=True,
    )

    _scheduler.start()
    logger.info(f"Scheduler started. chapter_check={chapter_cron!r}, recommendations={rec_cron!r}")
    return _scheduler


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        _scheduler = None


def reload_schedule() -> None:
    """Reload cron expressions from config and update running jobs."""
    global _scheduler
    config = reload_config()
    schedules = config.get("schedules", {})

    if _scheduler is None or not _scheduler.running:
        start_scheduler()
        return

    chapter_cron = schedules.get("chapter_check", "0 2 * * *")
    rec_cron = schedules.get("recommendations", "0 3 * * 1")

    _scheduler.reschedule_job("chapter_check", trigger=_parse_cron(chapter_cron))
    _scheduler.reschedule_job("recommendations", trigger=_parse_cron(rec_cron))
    logger.info(f"Schedule reloaded: chapter_check={chapter_cron!r}, recommendations={rec_cron!r}")


def trigger_now(job_id: str) -> None:
    """Immediately run a job by ID (for the 'Run Now' button in settings)."""
    if job_id == "chapter_check":
        run_chapter_check()
    elif job_id == "recommendations":
        run_recommendations()
    else:
        raise ValueError(f"Unknown job: {job_id!r}")


def get_scheduler() -> BackgroundScheduler | None:
    return _scheduler
