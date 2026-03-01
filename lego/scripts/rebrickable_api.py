from __future__ import annotations

from typing import Any, Iterator, Optional

import requests

from lego.scripts.load_credentials import get_rebrickable_headers


BASE_URL = "https://rebrickable.com/api/v3/lego"


class RebrickableClient:
    def __init__(self, api_key: Optional[str] = None, timeout: int = 30) -> None:
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"Authorization": f"key {api_key}"})
        else:
            self.session.headers.update(get_rebrickable_headers())
        self.timeout = timeout

    def get(self, path: str, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        url = f"{BASE_URL}/{path.lstrip('/')}"
        resp = self.session.get(url, params=params or {}, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def iter_list(self, path: str, params: Optional[dict[str, Any]] = None) -> Iterator[dict[str, Any]]:
        params = dict(params or {})
        url = f"{BASE_URL}/{path.lstrip('/')}"
        while True:
            resp = self.session.get(url, params=params, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            for item in data.get("results", []):
                yield item
            url = data.get("next")
            if not url:
                break
            params = None

    def search_sets(self, query: str, page_size: int = 20) -> dict[str, Any]:
        return self.get("sets/", params={"search": query, "page_size": page_size})

    def get_set(self, set_num: str) -> dict[str, Any]:
        return self.get(f"sets/{set_num}/")

    def get_set_parts(self, set_num: str, page_size: int = 1000) -> Iterator[dict[str, Any]]:
        return self.iter_list(f"sets/{set_num}/parts/", params={"page_size": page_size})
