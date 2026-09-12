"""add M15 and H4 continuous aggregates for analytics

Revision ID: 0005_prices_m15_h4
Revises: 0004_ywo_index_tickers
Create Date: 2026-09-12

Phase 2 W4·D1: metrics/regimes use M1, M15, H1, H4, D1.
H1/D1 already exist from 0001_initial.
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op

revision: str = "0005_prices_m15_h4"
down_revision: Union[str, None] = "0004_ywo_index_tickers"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("SET lock_timeout = '5s'")

    op.execute(
        """
        CREATE MATERIALIZED VIEW prices_m15
        WITH (timescaledb.continuous) AS
        SELECT
          symbol,
          time_bucket(INTERVAL '15 minutes', ts) AS bucket,
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
          'prices_m15',
          start_offset => INTERVAL '2 days',
          end_offset => INTERVAL '15 minutes',
          schedule_interval => INTERVAL '15 minutes',
          if_not_exists => TRUE
        )
        """
    )

    op.execute(
        """
        CREATE MATERIALIZED VIEW prices_h4
        WITH (timescaledb.continuous) AS
        SELECT
          symbol,
          time_bucket(INTERVAL '4 hours', ts) AS bucket,
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
          'prices_h4',
          start_offset => INTERVAL '14 days',
          end_offset => INTERVAL '4 hours',
          schedule_interval => INTERVAL '4 hours',
          if_not_exists => TRUE
        )
        """
    )


def downgrade() -> None:
    op.execute("SET lock_timeout = '5s'")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS prices_h4 CASCADE")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS prices_m15 CASCADE")
