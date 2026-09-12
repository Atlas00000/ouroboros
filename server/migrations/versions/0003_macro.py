"""add macro_observations table

Revision ID: 0003_macro
Revises: 0002_seed
Create Date: 2026-09-12
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003_macro"
down_revision: Union[str, None] = "0002_seed"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("SET lock_timeout = '5s'")
    op.create_table(
        "macro_observations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("series_id", sa.String(length=64), nullable=False),
        sa.Column("obs_date", sa.Date(), nullable=False),
        sa.Column("value", sa.Numeric(precision=24, scale=8), nullable=True),
        sa.Column("source", sa.String(length=32), nullable=False, server_default="fred"),
        sa.Column(
            "ingested_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("series_id", "obs_date", name="uq_macro_series_date"),
    )
    op.create_index(
        "ix_macro_series_date",
        "macro_observations",
        ["series_id", "obs_date"],
        unique=False,
    )


def downgrade() -> None:
    op.execute("SET lock_timeout = '5s'")
    op.drop_index("ix_macro_series_date", table_name="macro_observations")
    op.drop_table("macro_observations")
