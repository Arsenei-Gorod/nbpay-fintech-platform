from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase

from app.core.config import get_settings


class Base(DeclarativeBase):
    pass


_engine = None
_SessionLocal: sessionmaker[Session] | None = None


def _ensure_engine() -> tuple[sessionmaker[Session] | None, object | None]:
    global _engine, _SessionLocal
    if _SessionLocal is not None:
        return _SessionLocal, _engine
    settings = get_settings()
    if not settings.DATABASE_URL:
        return None, None
    _engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        future=True,
        echo=getattr(settings, "DB_ECHO", False),
    )
    _SessionLocal = sessionmaker(
        bind=_engine, autoflush=False, autocommit=False, future=True
    )
    return _SessionLocal, _engine


@contextmanager
def get_session() -> Iterator[Session]:
    SessionLocal, _ = _ensure_engine()
    if SessionLocal is None:
        raise RuntimeError("DATABASE_URL is not configured")
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def create_all() -> None:
    """Create database tables if engine available."""
    from app.infrastructure.models import user as user_model  # noqa: F401 - ensure models are imported

    SessionLocal, engine = _ensure_engine()
    if engine is not None:
        Base.metadata.create_all(bind=engine)
