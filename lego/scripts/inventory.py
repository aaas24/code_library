from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import csv

import duckdb

from .config import get_cache_dir


def _clean_csv_bom(src_path: Path) -> Path:
    cache_dir = get_cache_dir()
    cache_dir.mkdir(parents=True, exist_ok=True)
    dest_path = cache_dir / "my_sets.cleaned.csv"
    with src_path.open("r", encoding="utf-8-sig", newline="") as src, dest_path.open(
        "w", encoding="utf-8", newline=""
    ) as dst:
        reader = csv.reader(src)
        writer = csv.writer(dst)
        for row in reader:
            writer.writerow(row)
    return dest_path


def _read_headers(csv_path: Path) -> list[str]:
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        return [h.strip() for h in next(reader)]


def load_my_sets_from_csv(con: duckdb.DuckDBPyConnection, csv_path: Path) -> None:
    now = datetime.now(timezone.utc)
    cleaned_path = _clean_csv_bom(csv_path)
    headers = {h.lower() for h in _read_headers(cleaned_path)}

    def col_or_null(*names: str) -> str:
        for name in names:
            if name in headers:
                return name
        return "NULL"

    set_name_col = col_or_null("set_name", "name")
    set_number_col = col_or_null("set_number", "set_num")
    pieces_col = col_or_null("pieces")
    age_col = col_or_null("age")
    year_col = col_or_null("year")
    on_display_col = col_or_null("on_display")
    theme_col = col_or_null("theme")
    instructions_col = col_or_null("instructions_link")
    photo_col = col_or_null("photo_link")
    quantity_col = col_or_null("quantity")

    pieces_expr = f"TRY_CAST({pieces_col} AS INTEGER)" if pieces_col != "NULL" else "NULL"
    age_expr = f"TRY_CAST({age_col} AS INTEGER)" if age_col != "NULL" else "NULL"
    year_expr = f"TRY_CAST({year_col} AS INTEGER)" if year_col != "NULL" else "NULL"
    on_display_expr = (
        f"CAST({on_display_col} AS BOOLEAN)" if on_display_col != "NULL" else "FALSE"
    )
    quantity_expr = (
        f"TRY_CAST({quantity_col} AS INTEGER)" if quantity_col != "NULL" else "1"
    )

    model_id_expr = (
        f"TRY_CAST({set_number_col} AS INTEGER)" if set_number_col != "NULL" else "NULL"
    )
    set_num_expr = (
        f"""
        CASE
            WHEN {set_number_col} IS NULL THEN NULL
            WHEN instr(CAST({set_number_col} AS TEXT), '-') > 0
                THEN CAST({set_number_col} AS TEXT)
            ELSE CAST({set_number_col} AS TEXT) || '-1'
        END
        """
        if set_number_col != "NULL"
        else "NULL"
    )

    con.execute(
        f"""
        CREATE OR REPLACE TABLE my_sets AS
        SELECT
            {model_id_expr} AS model_id,
            'set' AS type,
            {set_num_expr} AS set_num,
            {set_name_col} AS set_name,
            {pieces_expr} AS pieces,
            {age_expr} AS age,
            {year_expr} AS year,
            {theme_col} AS theme,
            {instructions_col} AS instructions_link,
            {photo_col} AS photo_link,
            {quantity_expr} AS quantity,
            {on_display_expr} AS on_display,
            ? AS last_updated
        FROM read_csv_auto(?)
        """,
        [now, str(cleaned_path)],
    )


def seed_favorite_keywords(con: duckdb.DuckDBPyConnection) -> None:
    keywords = [
        "Harry Potter",
        "Deco",
        "Technic",
        "Love",
        "Nintendo",
        "Mario",
        "Yoshi",
        "Star Wars",
        "Architecture",
        "Art",
        "Botanicals",
        "Plants",
    ]
    con.execute("DELETE FROM favorite_keywords")
    con.executemany(
        "INSERT INTO favorite_keywords(keyword) VALUES (?)", [(k,) for k in keywords]
    )


def build_my_inventory(con: duckdb.DuckDBPyConnection) -> None:
    con.execute(
        """
        CREATE OR REPLACE TABLE my_inventory AS
        SELECT
            ip.part_num,
            ip.color_id,
            SUM(ip.quantity * ms.quantity) AS quantity
        FROM my_sets ms
        JOIN inventories i
          ON TRY_CAST(SPLIT_PART(CAST(i.set_num AS TEXT), '-', 1) AS INTEGER) = ms.model_id
        JOIN inventory_parts ip ON ip.inventory_id = i.id
        WHERE ms.on_display IS FALSE
          AND COALESCE(ip.is_spare, FALSE) IS FALSE
        GROUP BY ip.part_num, ip.color_id
        """
    )


def build_model_coverage(con: duckdb.DuckDBPyConnection) -> None:
    con.execute(
        """
        CREATE OR REPLACE TABLE model_coverage AS
        WITH owned AS (
            SELECT
                part_num,
                color_id,
                quantity AS owned_qty
            FROM my_inventory
        ),
        required AS (
            SELECT
                CAST(i.set_num AS TEXT) AS set_num,
                TRY_CAST(SPLIT_PART(CAST(i.set_num AS TEXT), '-', 1) AS INTEGER) AS model_id,
                ip.part_num,
                ip.color_id,
                ip.quantity AS req_qty
            FROM inventories i
            JOIN inventory_parts ip ON ip.inventory_id = i.id
            WHERE COALESCE(ip.is_spare, FALSE) IS FALSE
        )
        SELECT
            r.set_num,
            r.model_id,
            SUM(r.req_qty) AS total_required,
            SUM(
                CASE
                    WHEN o.owned_qty IS NULL THEN 0
                    WHEN o.owned_qty >= r.req_qty THEN r.req_qty
                    ELSE o.owned_qty
                END
            ) AS total_owned,
            CASE
                WHEN SUM(r.req_qty) = 0 THEN 0
                ELSE SUM(
                    CASE
                        WHEN o.owned_qty IS NULL THEN 0
                        WHEN o.owned_qty >= r.req_qty THEN r.req_qty
                        ELSE o.owned_qty
                    END
                ) / SUM(r.req_qty)
            END AS coverage_pct
        FROM required r
        LEFT JOIN owned o
          ON o.part_num = r.part_num
         AND o.color_id = r.color_id
        GROUP BY r.set_num, r.model_id
        """
    )


def build_candidate_models(con: duckdb.DuckDBPyConnection) -> None:
    con.execute(
        """
        CREATE OR REPLACE TABLE candidate_models AS
        SELECT
            s.set_num,
            s.name,
            mc.total_required,
            mc.total_owned,
            mc.coverage_pct
        FROM model_coverage mc
        LEFT JOIN sets s USING (set_num)
        LEFT JOIN my_sets m ON s.set_num = m.set_num
        WHERE mc.coverage_pct >= 0.85
          AND m.set_num IS NULL
          AND mc.total_required > 10
        ORDER BY mc.coverage_pct DESC
        """
    )
