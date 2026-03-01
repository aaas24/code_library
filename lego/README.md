Lego inventory helper (scaffold)

Goals
- Load Rebrickable CSV dumps into DuckDB.
- Store your owned sets in `my_sets`.
- Build a consolidated parts inventory from owned sets.
- Prepare for UI + API phases later.

Quick start
1) Create venv and install deps
   - `python -m venv .venv`
   - `source .venv/bin/activate`
   - `pip install -r lego/requirements.txt`
2) Initialize DB + seed favorite keywords
   - `python -m lego.scripts.cli init-db`
   - `python -m lego.scripts.cli seed-favorite-keywords`
3) Load Rebrickable CSV dumps
   - `python -m lego.scripts.cli load-rebrickable --all`
4) Load your owned sets
   - Prepare a CSV like:
     set_name,set_number,pieces,age,year,on_display,theme,instructions_link,photo_link,quantity
     buckbeak,76427,723,9,2024,false,harry potter,https://...,https://...,1
   - `set_number` should be an integer like `76427` (no `-1` suffix).
   - `set_num` will be stored with the `-1` suffix for Rebrickable joins.
   - `python -m lego.scripts.cli load-my-sets --csv /path/to/my_sets.csv`
   - If you set `RAW_FILES_PATH`, the CLI will look for `my_sets.csv` there.
5) Build your inventory
   - `python -m lego.scripts.cli build-inventory`
5.1) Refresh my_sets + inventory (no coverage)
   - `python -m lego.scripts.cli refresh-inventory`
6) Score coverage and rank candidate models
   - `python -m lego.scripts.cli build-coverage`
   - `python -m lego.scripts.cli build-candidates`
   - Query `candidate_models` for the ranked list (coverage >= 85%, not owned, >10 parts).

DB location
- Default: `~/lego.duckdb`
- Override with `LEGO_DB_PATH=/path/to/lego.duckdb`
- If `LEGO_DB_PATH` points to a directory, the DB will be created as `lego.duckdb` inside it.

Notebook usage (recommended)
```python
import duckdb
from pathlib import Path
from lego.scripts.inventory import load_my_sets_from_csv, build_my_inventory

con = duckdb.connect("/Users/alialvarez/Documents/databases/lego.duckdb")
load_my_sets_from_csv(con, Path("/Volumes/Datasets/lego/my_sets.csv"))
build_my_inventory(con)
```

Rebrickable API helpers (optional)
- Helpers live in `lego/scripts/`.
- Requires 1Password CLI (`op`) and an active session.
```python
from lego.scripts.rebrickable_api import RebrickableClient
client = RebrickableClient()
client.search_sets("Harry Potter", page_size=5)
```

SQL files
- Schema files live in `lego/sql/`.

What’s missing / to‑do
- Tkinter UI (browse candidates, trigger searches)
- API integration into the pipeline (store API results + parts locally)
- Better keyword matching (partial matches, weighting)
- Validation and reporting for `my_sets.csv`
- Automated refresh flow for notebook users

Notes
- API integration and UI are intentionally deferred.


Notebook output hygiene
- Outputs and execution counts are automatically stripped on save (Jupyter pre-save hook).
- A git pre-commit hook also strips outputs in `lego/notebooks/` to prevent accidental commits.
- Script: `lego/scripts/strip_notebooks.py`

