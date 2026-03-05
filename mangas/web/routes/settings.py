import logging

from flask import Blueprint, redirect, render_template, request, url_for

from utils.config_loader import load_config

logger = logging.getLogger(__name__)
bp = Blueprint("settings", __name__)


@bp.route("/settings")
def settings():
    config = load_config()
    return render_template("settings.html", config=config)


@bp.route("/settings/run-now", methods=["POST"])
def run_now():
    """Trigger an immediate crawl job."""
    job = request.form.get("job", "chapter_check")
    logger.info(f"Run-now triggered: job={job!r}")
    try:
        from scheduler.runner import trigger_now
        trigger_now(job)
        logger.info(f"Run-now dispatched: job={job!r}")
    except Exception as e:
        logger.error(f"Run-now failed for job={job!r}: {e}", exc_info=True)
    return redirect(url_for("settings.settings"))
