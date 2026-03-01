from __future__ import annotations

import os
from pathlib import Path


def get_db_path() -> Path:
    env_path = os.environ.get("LEGO_DB_PATH")
    if env_path:
        path = Path(env_path).expanduser()
        if path.suffix == "":
            return path / "lego.duckdb"
        return path
    return Path.home() / "lego.duckdb"


def get_cache_dir() -> Path:
    return Path(__file__).resolve().parents[1] / ".cache"
