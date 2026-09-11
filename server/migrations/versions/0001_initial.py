"""initial schema: tables, hypertable, compression, retention, caggs, outbox

Revision ID: 0001_initial
Revises:
Create Date: 2026-09-11
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("SET lock_timeout = '5s'")
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE")

    op.create_table(
        "assets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("display_name", sa.String(length=128), nullable=False),
        sa.Column("asset_class", sa.String(length=32), nullable=False),
        sa.Column("mt5_ticker", sa.String(length=64), nullable=True),
        sa.Column("base_currency", sa.String(length=16), nullable=True),
        sa.Column("quote_currency", sa.String(length=16), nullable=True),
        sa.Column("venues", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("symbol"),
    )
    op.create_index("ix_assets_symbol", "assets", ["symbol"])

    op.create_table(
        "prices",
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("open", sa.Numeric(18, 8), nullable=False),
        sa.Column("high", sa.Numeric(18, 8), nullable=False),
        sa.Column("low", sa.Numeric(18, 8), nullable=False),
        sa.Column("close", sa.Numeric(18, 8), nullable=False),
        sa.Column("volume", sa.Numeric(24, 8), nullable=False, server_default="0"),
        sa.Column("source", sa.String(length=32), nullable=False, server_default="mt5"),
        sa.Column("ingested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("tick_volume", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(["symbol"], ["assets.symbol"]),
        sa.PrimaryKeyConstraint("symbol", "ts"),
        sa.UniqueConstraint("symbol", "ts", name="uq_prices_symbol_ts"),
    )
    op.create_index("ix_prices_symbol_ts", "prices", ["symbol", "ts"])

    # Timescale hypertable + lifecycle policies
    op.execute("SELECT create_hypertable('prices', 'ts', if_not_exists => TRUE)")
    op.execute(
        """
        ALTER TABLE prices SET (
          timescaledb.compress,
          timescaledb.compress_segmentby = 'symbol',
          timescaledb.compress_orderby = 'ts DESC'
        )
        """
    )
    op.execute("SELECT add_compression_policy('prices', INTERVAL '7 days', if_not_exists => TRUE)")
    op.execute("SELECT add_retention_policy('prices', INTERVAL '5 years', if_not_exists => TRUE)")

    # Continuous aggregates H1 / D1
    op.execute(
        """
        CREATE MATERIALIZED VIEW prices_h1
        WITH (timescaledb.continuous) AS
        SELECT
          symbol,
          time_bucket(INTERVAL '1 hour', ts) AS bucket,
          first(open, ts) AS open,
          max(high) AS high,
          min(low) AS low,
          last(close, ts) AS close,
          sum(volume) AS volume
        FROM prices
        GROUP BY symbol, bucket
        WITH NO DATA
        """
    )
    op.execute(
        """
        SELECT add_continuous_aggregate_policy(
          'prices_h1',
          start_offset => INTERVAL '3 days',
          end_offset => INTERVAL '1 hour',
          schedule_interval => INTERVAL '1 hour',
          if_not_exists => TRUE
        )
        """
    )
    op.execute(
        """
        CREATE MATERIALIZED VIEW prices_d1
        WITH (timescaledb.continuous) AS
        SELECT
          symbol,
          time_bucket(INTERVAL '1 day', ts) AS bucket,
          first(open, ts) AS open,
          max(high) AS high,
          min(low) AS low,
          last(close, ts) AS close,
          sum(volume) AS volume
        FROM prices
        GROUP BY symbol, bucket
        WITH NO DATA
        """
    )
    op.execute(
        """
        SELECT add_continuous_aggregate_policy(
          'prices_d1',
          start_offset => INTERVAL '30 days',
          end_offset => INTERVAL '1 day',
          schedule_interval => INTERVAL '1 day',
          if_not_exists => TRUE
        )
        """
    )

    op.create_table(
        "news",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("external_id", sa.String(length=128), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=True),
        sa.Column("headline", sa.Text(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=True),
        sa.Column("impact", sa.String(length=16), nullable=True),
        sa.Column("is_calendar", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "ingested_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("external_id"),
    )
    op.create_index("ix_news_published_at", "news", ["published_at"])
    op.create_index("ix_news_symbol", "news", ["symbol"])

    op.create_table(
        "sentiment",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("score", sa.Numeric(6, 4), nullable=False),
        sa.Column("item_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("window_hours", sa.Integer(), nullable=False, server_default="24"),
        sa.Column("top_drivers_json", sa.Text(), nullable=True),
        sa.Column("as_of", sa.DateTime(timezone=True), nullable=False),
        sa.Column("model_version", sa.String(length=64), nullable=False),
        sa.Column("confidence", sa.Numeric(5, 4), nullable=False, server_default="0"),
        sa.Column("stale", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("sources_json", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["symbol"], ["assets.symbol"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sentiment_symbol_as_of", "sentiment", ["symbol", "as_of"])

    op.create_table(
        "states",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("timeframe", sa.String(length=8), nullable=False),
        sa.Column("regime", sa.String(length=32), nullable=False),
        sa.Column("probabilities_json", sa.Text(), nullable=False),
        sa.Column("volatility_percentile", sa.Numeric(6, 2), nullable=True),
        sa.Column("trend_strength", sa.Numeric(6, 4), nullable=True),
        sa.Column("as_of", sa.DateTime(timezone=True), nullable=False),
        sa.Column("model_version", sa.String(length=64), nullable=False),
        sa.Column("confidence", sa.Numeric(5, 4), nullable=False, server_default="0"),
        sa.Column("stale", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("sources_json", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["symbol"], ["assets.symbol"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_states_symbol_tf_as_of", "states", ["symbol", "timeframe", "as_of"])

    op.create_table(
        "profiles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("profile_version", sa.Integer(), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("as_of", sa.DateTime(timezone=True), nullable=False),
        sa.Column("model_version", sa.String(length=64), nullable=False),
        sa.Column("confidence", sa.Numeric(5, 4), nullable=False, server_default="0"),
        sa.Column("stale", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["symbol"], ["assets.symbol"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("symbol", "profile_version", name="uq_profiles_symbol_ver"),
    )

    op.create_table(
        "insights",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=True),
        sa.Column("insight_type", sa.String(length=32), nullable=False, server_default="narrative"),
        sa.Column("title", sa.String(length=256), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("tags_json", sa.Text(), nullable=True),
        sa.Column("related_refs_json", sa.Text(), nullable=True),
        sa.Column("as_of", sa.DateTime(timezone=True), nullable=False),
        sa.Column("model_version", sa.String(length=64), nullable=False),
        sa.Column("confidence", sa.Numeric(5, 4), nullable=False, server_default="0"),
        sa.Column("stale", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("sources_json", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_insights_symbol_as_of", "insights", ["symbol", "as_of"])

    op.create_table(
        "source_registry",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("kind", sa.String(length=32), nullable=False),
        sa.Column("expected_cadence_seconds", sa.Integer(), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="unknown"),
        sa.Column("license_notes", sa.Text(), nullable=True),
        sa.Column("meta_json", sa.Text(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_id"),
    )

    op.create_table(
        "forecast_log",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("timeframe", sa.String(length=8), nullable=False),
        sa.Column("call_type", sa.String(length=32), nullable=False),
        sa.Column("prediction_json", sa.Text(), nullable=False),
        sa.Column("model_version", sa.String(length=64), nullable=False),
        sa.Column("confidence", sa.Numeric(5, 4), nullable=False, server_default="0"),
        sa.Column("made_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("horizon_minutes", sa.Integer(), nullable=True),
        sa.Column("realized_json", sa.Text(), nullable=True),
        sa.Column("scored_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("score", sa.Numeric(8, 4), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_forecast_log_symbol_made_at", "forecast_log", ["symbol", "made_at"])

    op.create_table(
        "outbox",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("event_id", sa.String(length=64), nullable=False),
        sa.Column("event", sa.String(length=64), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("publish_attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_id"),
    )
    op.create_index("ix_outbox_unpublished", "outbox", ["published_at", "id"])
    op.create_index("ix_outbox_event", "outbox", ["event"])


def downgrade() -> None:
    op.execute("SET lock_timeout = '5s'")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS prices_d1 CASCADE")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS prices_h1 CASCADE")
    op.drop_table("outbox")
    op.drop_table("forecast_log")
    op.drop_table("source_registry")
    op.drop_table("insights")
    op.drop_table("profiles")
    op.drop_table("states")
    op.drop_table("sentiment")
    op.drop_table("news")
    op.drop_table("prices")
    op.drop_table("assets")
