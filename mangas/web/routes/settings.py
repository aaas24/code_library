from flask import Blueprint, redirect, render_template, request, url_for

from utils.config_loader import load_config

bp = Blueprint("settings", __name__)


@bp.route("/settings")
def settings():
    config = load_config()
    return render_template("settings.html", config=config)


@bp.route("/settings/run-now", methods=["POST"])
def run_now():
    """Trigger an immediate crawl job."""
    job = request.form.get("job", "chapter_check")
    try:
        from scheduler.runner import trigger_now
        trigger_now(job)
    except Exception as e:
        pass  # Log but don't crash the UI
    return redirect(url_for("settings.settings"))
