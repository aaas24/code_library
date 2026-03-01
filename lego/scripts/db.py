from __future__ import annotations

from pathlib import Path
import duckdb


def connect(db_path: Path) -> duckdb.DuckDBPyConnection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(db_path))


def init_db(con: duckdb.DuckDBPyConnection) -> None:
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS my_sets (
            model_id INTEGER,
            type TEXT,
            set_num TEXT,
            set_name TEXT,
            pieces INTEGER,
            age INTEGER,
            year INTEGER,
            theme TEXT,
            instructions_link TEXT,
            photo_link TEXT,
            quantity INTEGER,
            on_display BOOLEAN,
            last_updated TIMESTAMP
        );
        """
    )
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS favorite_keywords (
            keyword TEXT
        );
        """
    )
