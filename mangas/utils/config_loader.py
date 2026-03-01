"""Loads and validates config.yaml on startup."""
from pathlib import Path

import yaml

from config_schema import validate_config

_CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"
_config_cache: dict | None = None


def load_config(path: str | None = None) -> dict:
    """Load config.yaml, validate it, and return the dict. Cached after first load."""
    global _config_cache
    if _config_cache is not None and path is None:
        return _config_cache

    config_path = Path(path) if path else _CONFIG_PATH
    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    validate_config(config)
    if path is None:
        _config_cache = config
    return config


def reload_config(path: str | None = None) -> dict:
    """Force reload config from disk."""
    global _config_cache
    _config_cache = None
    return load_config(path)
