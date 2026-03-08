"""SQLAlchemy models for the manga tracker."""
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, Text, create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


class Manga(Base):
    __tablename__ = "manga"

    id = Column(Integer, primary_key=True)
    url = Column(Text, unique=True, nullable=False)
    title = Column(Text)
    site = Column(Text)
    last_episode_published = Column(Integer)
    last_episode_read = Column(Integer)
    # status: active | didnt_love | finished | pass
    status = Column(Text, default="active")
    has_update = Column(Boolean, default=False)
    is_favorite = Column(Boolean, default=False)
    last_checked = Column(DateTime)
    last_read_at = Column(DateTime)
    raw_note = Column(Text)
    bug_type = Column(Text, nullable=True)
    corrected_from = Column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<Manga id={self.id} title={self.title!r} status={self.status}>"


class Recommendation(Base):
    __tablename__ = "recommendation"

    id = Column(Integer, primary_key=True)
    url = Column(Text, unique=True, nullable=False)
    title = Column(Text)
    site = Column(Text)
    chapter_count = Column(Integer)
    matched_themes = Column(Text)  # JSON array stored as string
    score = Column(Integer, default=0)
    seen = Column(Boolean, default=False)
    discovered_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Recommendation id={self.id} title={self.title!r} score={self.score}>"


def get_engine(db_path: str = "data/mangas.db"):
    return create_engine(f"sqlite:///{db_path}", echo=False)


def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()


def init_db(db_path: str = "data/mangas.db"):
    engine = get_engine(db_path)
    Base.metadata.create_all(engine)
    # Migrate existing DBs: add columns introduced after initial schema
    with engine.connect() as conn:
        for stmt in (
            "ALTER TABLE manga ADD COLUMN is_favorite BOOLEAN DEFAULT 0",
            "ALTER TABLE manga ADD COLUMN last_read_at DATETIME",
            "ALTER TABLE manga ADD COLUMN bug_type TEXT",
            "ALTER TABLE manga ADD COLUMN corrected_from TEXT",
        ):
            try:
                conn.execute(text(stmt))
                conn.commit()
            except Exception:
                pass  # column already exists
    # Data fixes applied on every startup (idempotent)
    import re
    from utils.manga_url import canonical_manga_url, clean_page_title
    _KALI_ID_RE = re.compile(r"^\d+\s+")
    _CHAPTER_PATH_RE = re.compile(r"/chapter", re.IGNORECASE)
    with engine.connect() as conn:
        # Fix 1a: strip leading numeric IDs from stored kaliscan.io titles
        rows = conn.execute(text("SELECT id, title FROM manga WHERE site = 'kaliscan.io' AND title IS NOT NULL")).fetchall()
        for row in rows:
            if _KALI_ID_RE.match(row[1]):
                clean = _KALI_ID_RE.sub("", row[1]).strip()
                conn.execute(text("UPDATE manga SET title = :t WHERE id = :id"), {"t": clean, "id": row[0]})

        # Fix 1b: derive title from URL slug for kaliscan records with no title
        rows = conn.execute(text("SELECT id, url FROM manga WHERE site = 'kaliscan.io' AND title IS NULL")).fetchall()
        for row in rows:
            slug = row[1].rstrip("/").split("/")[-1]
            title = _KALI_ID_RE.sub("", slug.replace("-", " ").replace("_", " ")).strip().title()
            if title:
                conn.execute(text("UPDATE manga SET title = :t WHERE id = :id"), {"t": title, "id": row[0]})

        # Fix 2: canonicalize chapter URLs → manga root URL
        rows = conn.execute(text("SELECT id, url FROM manga WHERE url LIKE '%/chapter%'")).fetchall()
        for row in rows:
            canon = canonical_manga_url(row[1])
            if canon != row[1]:
                conn.execute(text("UPDATE manga SET url = :u WHERE id = :id"), {"u": canon, "id": row[0]})

        # Fix 3: strip " - Chapter N..." from titles
        rows = conn.execute(text("SELECT id, title FROM manga WHERE title LIKE '% - Chapter %' OR title LIKE '% - chapter %'")).fetchall()
        for row in rows:
            if row[1]:
                clean = clean_page_title(row[1])
                if clean != row[1]:
                    conn.execute(text("UPDATE manga SET title = :t WHERE id = :id"), {"t": clean, "id": row[0]})

        conn.commit()
    return engine
