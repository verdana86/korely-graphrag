"""Database engine, session factory, and bootstrap helpers."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from ..config import get_settings
from .models import Base, create_extensions

_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(get_settings().database_url, future=True, pool_pre_ping=True)
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine(), expire_on_commit=False, future=True)
    return _SessionLocal


@contextmanager
def session_scope() -> Iterator[Session]:
    """Transactional session: commits on success, rolls back on exception."""
    session = get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db(*, drop_first: bool = False) -> None:
    """Create the schema. Idempotent: safe to call repeatedly.

    With `drop_first=True`, drops all tables first — destructive, used by
    `korely-graphrag ingest --reset` and by integration tests.
    """
    engine = get_engine()
    with engine.begin() as conn:
        create_extensions(conn)
        if drop_first:
            Base.metadata.drop_all(bind=conn)
        Base.metadata.create_all(bind=conn)


def healthcheck() -> bool:
    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def reset_engine_for_tests() -> None:
    """Force engine/session re-creation. Tests use this between fixtures."""
    global _engine, _SessionLocal
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _SessionLocal = None
