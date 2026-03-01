from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable


def strip_notebook(path: Path) -> bool:
    data = json.loads(path.read_text())
    changed = False
    for cell in data.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        if cell.get("outputs"):
            cell["outputs"] = []
            changed = True
        if cell.get("execution_count") is not None:
            cell["execution_count"] = None
            changed = True
    if changed:
        path.write_text(json.dumps(data, indent=1))
    return changed


def iter_notebooks(base: Path) -> Iterable[Path]:
    if base.is_file() and base.suffix == ".ipynb":
        yield base
        return
    for path in base.rglob("*.ipynb"):
        if ".ipynb_checkpoints" in path.parts:
            continue
        yield path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    notebooks_dir = repo_root / "lego" / "notebooks"
    changed_any = False
    for nb in iter_notebooks(notebooks_dir):
        changed_any = strip_notebook(nb) or changed_any
    return 1 if changed_any else 0


if __name__ == "__main__":
    raise SystemExit(main())
