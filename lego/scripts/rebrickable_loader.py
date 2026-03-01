from __future__ import annotations

import io
import urllib.request
import zipfile
from pathlib import Path

import duckdb

from .config import get_cache_dir

DATASETS = {
    "themes": "https://cdn.rebrickable.com/media/downloads/themes.csv.zip",
    "colors": "https://cdn.rebrickable.com/media/downloads/colors.csv.zip",
    "part_categories": "https://cdn.rebrickable.com/media/downloads/part_categories.csv.zip",
    "parts": "https://cdn.rebrickable.com/media/downloads/parts.csv.zip",
    "part_relationships": "https://cdn.rebrickable.com/media/downloads/part_relationships.csv.zip",
    "elements": "https://cdn.rebrickable.com/media/downloads/elements.csv.zip",
    "sets": "https://cdn.rebrickable.com/media/downloads/sets.csv.zip",
    "minifigs": "https://cdn.rebrickable.com/media/downloads/minifigs.csv.zip",
    "inventories": "https://cdn.rebrickable.com/media/downloads/inventories.csv.zip",
    "inventory_parts": "https://cdn.rebrickable.com/media/downloads/inventory_parts.csv.zip",
    "inventory_sets": "https://cdn.rebrickable.com/media/downloads/inventory_sets.csv.zip",
    "inventory_minifigs": "https://cdn.rebrickable.com/media/downloads/inventory_minifigs.csv.zip",
}


def _download_zip(url: str, dest_path: Path) -> None:
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as response:
        data = response.read()
    dest_path.write_bytes(data)


def _extract_first_csv(zip_path: Path) -> bytes:
    with zipfile.ZipFile(zip_path, "r") as zf:
        csv_names = [n for n in zf.namelist() if n.endswith(".csv")]
        if not csv_names:
            raise ValueError(f"No CSV found in {zip_path}")
        return zf.read(csv_names[0])


def load_dataset(con: duckdb.DuckDBPyConnection, name: str, force: bool = False) -> None:
    if name not in DATASETS:
        raise KeyError(f"Unknown dataset: {name}")
    cache_dir = get_cache_dir()
    zip_path = cache_dir / f"{name}.csv.zip"
    if force or not zip_path.exists():
        _download_zip(DATASETS[name], zip_path)

    csv_bytes = _extract_first_csv(zip_path)
    csv_file = cache_dir / f"{name}.csv"
    csv_file.write_bytes(csv_bytes)

    con.execute(f"CREATE OR REPLACE TABLE {name} AS SELECT * FROM read_csv_auto(?)", [str(csv_file)])


def load_all(con: duckdb.DuckDBPyConnection, force: bool = False) -> None:
    for name in DATASETS:
        load_dataset(con, name, force=force)
