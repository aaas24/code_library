"""Auto-discovers crawlers and maps domain → crawler class."""
import importlib
import pkgutil
from pathlib import Path
from typing import Optional

from crawler.base import BaseCrawler

_REGISTRY: dict[str, type[BaseCrawler]] = {}
_discovered = False


def _discover() -> None:
    global _discovered
    if _discovered:
        return
    _discovered = True

    package_dir = Path(__file__).parent
    package_name = "crawler"

    for finder, module_name, is_pkg in pkgutil.iter_modules([str(package_dir)]):
        if module_name in ("base", "registry"):
            continue
        importlib.import_module(f"{package_name}.{module_name}")

    for cls in BaseCrawler.__subclasses__():
        if cls.domain:
            _REGISTRY[cls.domain] = cls
            for extra in cls.extra_domains:
                _REGISTRY[extra] = cls


def get_crawler(domain: str) -> Optional[BaseCrawler]:
    _discover()
    cls = _REGISTRY.get(domain)
    return cls() if cls else None


def all_crawlers() -> list[BaseCrawler]:
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
