"""Alembic environment — migration-first governance."""

from __future__ import annotations

from logging.config import fileConfig

import app.models  # noqa: F401 — register models on metadata
from alembic import context
from sqlalchemy import engine_from_config, pool, text

from app.config import get_settings
from app.db.base import Base
from app.db.session import _normalize_url

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url() -> str:
    return _normalize_url(get_settings().database_url)


def include_object(object, name, type_, reflected, compare_to) -> bool:  # noqa: ANN001, A002
    """Ignore Timescale-managed / redundant objects not owned by ORM metadata."""
    if type_ == "index" and name in {"prices_ts_idx"}:
        return False
    # Redundant with composite PK; kept in DB from 0001 for safety, ignore in drift checks
    if type_ == "unique_constraint" and name in {"uq_prices_symbol_ts"}:
        return False
    return True


def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        connection.execute(text("SET lock_timeout = '5s'"))
        connection.commit()
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            include_object=include_object,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
