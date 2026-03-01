"""Validates the import results before retiring Mangas.md.

Usage:
    python import/validate_import.py          # review only
    python import/validate_import.py --confirm  # lock import, mark Mangas.md retired
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import db.ops as ops
from db.models import get_engine, get_session, Manga

RETIRED_MARKER = Path(__file__).parent.parent / "data" / "import" / "RETIRED"


def _print_summary(session):
    total = session.query(Manga).count()
    by_status = {}
    for m in session.query(Manga).all():
        by_status.setdefault(m.status, 0)
        by_status[m.status] += 1

    with_published = session.query(Manga).filter(Manga.last_episode_published.isnot(None)).count()
    with_read = session.query(Manga).filter(Manga.last_episode_read.isnot(None)).count()
    with_updates = session.query(Manga).filter(Manga.has_update.is_(True)).count()

    print(f"\n{'='*50}")
    print(f"IMPORT SUMMARY")
    print(f"{'='*50}")
    print(f"Total manga:        {total}")
    for status, count in sorted(by_status.items()):
        print(f"  {status:<20} {count}")
    print(f"With chapter data:  {with_published} published / {with_read} read")
    print(f"Has updates:        {with_updates}")
    print(f"{'='*50}")


def _print_sample(session, status: str, limit: int = 5):
    rows = session.query(Manga).filter_by(status=status).limit(limit).all()
    if not rows:
        return
    print(f"\nSample [{status}]:")
    for m in rows:
        pub = m.last_episode_published or "?"
        read = m.last_episode_read or "?"
        note = f" [{m.raw_note}]" if m.raw_note else ""
        print(f"  {m.url[:60]:<60}  pub={pub}  read={read}{note}")


def main():
    confirm = "--confirm" in sys.argv

    if RETIRED_MARKER.exists():
        print("Import is already confirmed and locked. Mangas.md is retired.")
        sys.exit(0)

    ops.init()
    engine = ops._engine
    session = get_session(engine)

    try:
        _print_summary(session)
        for status in ("active", "didnt_love", "finished", "pass"):
            _print_sample(session, status)

        if not confirm:
            print("\nRun with --confirm to lock the import and retire Mangas.md.")
            return

        # Write the retired marker
        RETIRED_MARKER.parent.mkdir(parents=True, exist_ok=True)
        RETIRED_MARKER.write_text(
            "Import confirmed. Mangas.md is retired. SQLite is now the source of truth.\n"
        )
        print("\n✓ Import confirmed. RETIRED marker written.")
        print("  SQLite is now the source of truth. Do not run the import again.")

    finally:
        session.close()


if __name__ == "__main__":
    main()
