"""Flask app factory."""
import logging
import os

from flask import Flask

import db.ops as ops
from utils.config_loader import load_config

logger = logging.getLogger(__name__)


def create_app(db_path: str | None = None, testing: bool = False) -> Flask:
    app = Flask(__name__, template_folder="templates")

    # Secret key — from 1Password in production, env var in tests
    if testing:
        app.secret_key = "test-secret-key"
    else:
        try:
            from utils.secrets import get_secret
            app.secret_key = get_secret("flask_secret_key")
        except Exception:
            app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-fallback-secret")

    # Init DB
    _db_path = db_path or "data/mangas.db"
    ops.init(_db_path)

    # Register blueprints
    from web.routes.dashboard import bp as dashboard_bp
    from web.routes.updates import bp as updates_bp
    from web.routes.active import bp as active_bp
    from web.routes.recommendations import bp as recommendations_bp
    from web.routes.read import bp as read_bp
    from web.routes.settings import bp as settings_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(updates_bp)
    app.register_blueprint(active_bp)
    app.register_blueprint(recommendations_bp)
    app.register_blueprint(read_bp)
    app.register_blueprint(settings_bp)

    # Start scheduler (skip in test mode)
    if not testing:
        try:
            from scheduler.runner import start_scheduler
            start_scheduler()
        except Exception as e:
            logger.warning(f"Scheduler start failed: {e}")

    return app


def main():
    config = load_config()
    web_cfg = config.get("web", {})
    host = web_cfg.get("host", "0.0.0.0")
    port = web_cfg.get("port", 5000)

    logging.basicConfig(level=logging.INFO)
    app = create_app()
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    main()
