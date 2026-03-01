"""Shared fixtures for pytest."""
import os
import sys
from pathlib import Path

import pytest

# Ensure project root is on sys.path so imports work from tests/
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))


@pytest.fixture
def tmp_db(tmp_path):
    """Return a temporary SQLite DB path and init the schema."""
    import db.ops as ops
    from db.models import init_db

    db_path = str(tmp_path / "test.db")
    ops._engine = None  # Reset module-level engine
    ops.init(db_path)
    yield db_path
    ops._engine = None


@pytest.fixture
def app(tmp_db):
    """Flask test app with a fresh in-memory DB."""
    from web.app import create_app

    application = create_app(db_path=tmp_db, testing=True)
    application.config["TESTING"] = True
    return application


@pytest.fixture
def client(app):
    return app.test_client()
