"""Engine and session factory."""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings

_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None


def _normalize_url(url: str) -> str:
    """Prefer psycopg3 driver for SQLAlchemy."""
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    return url


def get_engine() -> Engine:
    global _engine, _SessionLocal
    if _engine is None:
        settings = get_settings()
        _engine = create_engine(
            _normalize_url(settings.database_url),
            pool_pre_ping=True,
            pool_size=max(1, int(settings.db_pool_size)),
            max_overflow=max(0, int(settings.db_max_overflow)),
        )

        @event.listens_for(_engine, "connect")
        def _set_lock_timeout(dbapi_conn, _connection_record) -> None:  # type: ignore[no-untyped-def]
            # Avoid long locks on hypertables during migrations / DDL (roadmap N3).
            with dbapi_conn.cursor() as cur:
                cur.execute("SET lock_timeout = '5s'")

        _SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False)
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    get_engine()
    assert _SessionLocal is not None
    return _SessionLocal


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency — yields a request-scoped session."""
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()


def ping_db() -> bool:
    with get_engine().connect() as conn:
        conn.execute(text("SELECT 1"))
    return True
