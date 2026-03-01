from __future__ import annotations

import argparse
import os
from pathlib import Path

from .config import get_db_path
from .db import connect, init_db
from .inventory import (
    build_candidate_models,
    build_model_coverage,
    build_my_inventory,
    load_my_sets_from_csv,
    seed_favorite_keywords,
)
from .rebrickable_loader import DATASETS, load_all, load_dataset


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Lego inventory helper")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init-db")

    seed = sub.add_parser("seed-favorite-keywords")

    load_rb = sub.add_parser("load-rebrickable")
    load_rb.add_argument("--all", action="store_true")
    load_rb.add_argument("--dataset", choices=sorted(DATASETS.keys()))
    load_rb.add_argument("--force", action="store_true")

    load_ms = sub.add_parser("load-my-sets")
    load_ms.add_argument("--csv")

    sub.add_parser("build-inventory")
    sub.add_parser("build-coverage")
    sub.add_parser("build-candidates")
    sub.add_parser("refresh-inventory")

    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    db_path = get_db_path()
    con = connect(db_path)

    if args.cmd == "init-db":
        init_db(con)
    elif args.cmd == "seed-favorite-keywords":
        seed_favorite_keywords(con)
    elif args.cmd == "load-rebrickable":
        if args.all:
            load_all(con, force=args.force)
        elif args.dataset:
            load_dataset(con, args.dataset, force=args.force)
        else:
            raise SystemExit("Provide --all or --dataset")
    elif args.cmd == "load-my-sets":
        csv_path = args.csv
        if not csv_path:
            raw_dir = os.environ.get("RAW_FILES_PATH")
            if raw_dir:
                csv_path = str(Path(raw_dir) / "my_sets.csv")
        if not csv_path:
            raise SystemExit("Provide --csv or set RAW_FILES_PATH")
        load_my_sets_from_csv(con, Path(csv_path))
    elif args.cmd == "build-inventory":
        build_my_inventory(con)
    elif args.cmd == "build-coverage":
        build_model_coverage(con)
    elif args.cmd == "build-candidates":
        build_candidate_models(con)
    elif args.cmd == "refresh-inventory":
        raw_dir = os.environ.get("RAW_FILES_PATH")
        if not raw_dir:
            raise SystemExit("Set RAW_FILES_PATH or use load-my-sets with --csv")
        load_my_sets_from_csv(con, Path(raw_dir) / "my_sets.csv")
        build_my_inventory(con)
    else:
        raise SystemExit(f"Unknown command: {args.cmd}")


if __name__ == "__main__":
    main()
