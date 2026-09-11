"""Phase 0 database / seed / Timescale assertions (requires Docker services)."""

from __future__ import annotations

import pytest
from sqlalchemy import text

from app.db.session import get_engine


@pytest.fixture(scope="module")
def conn():
    engine = get_engine()
    connection = engine.connect()
    yield connection
    connection.close()


def test_alembic_head(conn) -> None:
    version = conn.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
    assert version == "0002_seed"


def test_core_tables_exist(conn) -> None:
    tables = {
        row[0]
        for row in conn.execute(
            text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
        )
    }
    expected = {
        "assets",
        "prices",
        "news",
        "sentiment",
        "states",
        "profiles",
        "insights",
        "source_registry",
        "forecast_log",
        "outbox",
        "alembic_version",
    }
    assert expected.issubset(tables)


def test_prices_is_hypertable(conn) -> None:
    rows = conn.execute(
        text("SELECT hypertable_name FROM timescaledb_information.hypertables")
    ).fetchall()
    assert "prices" in {r[0] for r in rows}


def test_continuous_aggregates(conn) -> None:
    rows = conn.execute(
        text("SELECT view_name FROM timescaledb_information.continuous_aggregates")
    ).fetchall()
    names = {r[0] for r in rows}
    assert "prices_h1" in names
    assert "prices_d1" in names


def test_seeded_asset_universe(conn) -> None:
    count = conn.execute(text("SELECT count(*) FROM assets WHERE is_active")).scalar_one()
    assert count >= 15
    symbols = {
        row[0]
        for row in conn.execute(text("SELECT symbol FROM assets")).fetchall()
    }
    for required in ("EURUSD", "XAUUSD", "US500"):
        assert required in symbols


def test_seeded_source_registry(conn) -> None:
    count = conn.execute(text("SELECT count(*) FROM source_registry")).scalar_one()
    assert count >= 4
    ids = {
        row[0]
        for row in conn.execute(text("SELECT source_id FROM source_registry")).fetchall()
    }
    assert "mt5.prices" in ids
    assert "fred.macro" in ids


def test_outbox_table_ready(conn) -> None:
    # empty but writable shape
    cols = {
        row[0]
        for row in conn.execute(
            text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name = 'outbox'"
            )
        )
    }
    assert {"event_id", "event", "payload_json", "published_at"}.issubset(cols)
