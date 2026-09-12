"""profile retention index + prune function (180d then last-of-day)

Revision ID: 0006_profile_retention
Revises: 0005_prices_m15_h4
Create Date: 2026-09-12

Phase 2 W5·D2: keep every profile version for 180 days, then prune older
rows to the last version per UTC calendar day per symbol.
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op

revision: str = "0006_profile_retention"
down_revision: Union[str, None] = "0005_prices_m15_h4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("SET lock_timeout = '5s'")

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_profiles_symbol_created
        ON profiles (symbol, created_at DESC)
        """
    )

    # Callable by worker/cron: SELECT prune_profiles_retention(180);
    op.execute(
        """
        CREATE OR REPLACE FUNCTION prune_profiles_retention(p_retention_days integer DEFAULT 180)
        RETURNS integer
        LANGUAGE plpgsql
        AS $$
        DECLARE
          deleted integer;
          cutoff timestamptz := now() - make_interval(days => p_retention_days);
        BEGIN
          WITH ranked AS (
            SELECT
              id,
              ROW_NUMBER() OVER (
                PARTITION BY symbol, ((created_at AT TIME ZONE 'UTC')::date)
                ORDER BY created_at DESC, id DESC
              ) AS rn
            FROM profiles
            WHERE created_at < cutoff
          ),
          doomed AS (
            SELECT id FROM ranked WHERE rn > 1
          )
          DELETE FROM profiles p
          USING doomed d
          WHERE p.id = d.id;

          GET DIAGNOSTICS deleted = ROW_COUNT;
          RETURN deleted;
        END;
        $$
        """
    )


def downgrade() -> None:
    op.execute("SET lock_timeout = '5s'")
    op.execute("DROP FUNCTION IF EXISTS prune_profiles_retention(integer)")
    op.execute("DROP INDEX IF EXISTS ix_profiles_symbol_created")
