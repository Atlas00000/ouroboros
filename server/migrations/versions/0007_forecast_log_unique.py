"""forecast_log idempotency unique index (symbol, tf, call_type, made_at, model)

Revision ID: 0007_forecast_log_unique
Revises: 0006_profile_retention
Create Date: 2026-09-12

Phase 2 W5·D3: immutable append with de-dupe for the same bar classification.
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op

revision: str = "0007_forecast_log_unique"
down_revision: Union[str, None] = "0006_profile_retention"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("SET lock_timeout = '5s'")
    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS uq_forecast_log_call_identity
        ON forecast_log (symbol, timeframe, call_type, made_at, model_version)
        """
    )


def downgrade() -> None:
    op.execute("SET lock_timeout = '5s'")
    op.execute("DROP INDEX IF EXISTS uq_forecast_log_call_identity")
