"""Auto-discovers scrapers and maps domain → scraper class.

Any module in the scrapers/ package that defines a subclass of BaseScraper
with a non-empty `domain` is automatically registered on import.
"""
import importlib
import pkgutil
from pathlib import Path
from typing import Optional

from scrapers.base import BaseScraper

# Populated by _discover()
_REGISTRY: dict[str, type[BaseScraper]] = {}
_discovered = False


def _discover() -> None:
    global _discovered
    if _discovered:
        return
    _discovered = True

    package_dir = Path(__file__).parent
    package_name = "scrapers"

    for finder, module_name, is_pkg in pkgutil.iter_modules([str(package_dir)]):
        if module_name in ("base", "registry"):
            continue
        importlib.import_module(f"{package_name}.{module_name}")

    # Register all BaseScraper subclasses found
    for cls in BaseScraper.__subclasses__():
        if cls.domain:
            _REGISTRY[cls.domain] = cls
            for extra in cls.extra_domains:
                _REGISTRY[extra] = cls


def get_scraper(domain: str) -> Optional[BaseScraper]:
    """Return an instantiated scraper for the given domain, or None."""
    _discover()
    cls = _REGISTRY.get(domain)
    if cls:
        return cls()
    return None


def all_scrapers() -> list[BaseScraper]:
    """Return one instance of each registered scraper (for iterating all sites)."""
    _discover()
    seen = set()
    result = []
    for cls in _REGISTRY.values():
        if cls not in seen:
            seen.add(cls)
            result.append(cls())
    return result


def registered_domains() -> list[str]:
    _discover()
    return list(_REGISTRY.keys())
