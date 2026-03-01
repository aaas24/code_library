"""SQLAlchemy models for the manga tracker."""
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, create_engine
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
    last_checked = Column(DateTime)
    raw_note = Column(Text)

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
    return engine
