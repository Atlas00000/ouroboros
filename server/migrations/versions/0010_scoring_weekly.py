"""scoring_weekly_reports for W8 accuracy digests

Revision ID: 0010_scoring_weekly
Revises: 0009_article_scores
Create Date: 2026-09-13
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0010_scoring_weekly"
down_revision: Union[str, None] = "0009_article_scores"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("SET lock_timeout = '5s'")
    op.create_table(
        "scoring_weekly_reports",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("week_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("week_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("n_scored", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("n_correct", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("accuracy", sa.Numeric(6, 4), nullable=True),
        sa.Column("report_json", sa.Text(), nullable=False),
        sa.Column("email_sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_scoring_weekly_week_start",
        "scoring_weekly_reports",
        ["week_start"],
    )


def downgrade() -> None:
    op.execute("SET lock_timeout = '5s'")
    op.drop_index("ix_scoring_weekly_week_start", table_name="scoring_weekly_reports")
    op.drop_table("scoring_weekly_reports")
