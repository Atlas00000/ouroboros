"""article sentiment score cache (never re-score same headline)

Revision ID: 0009_article_scores
Revises: 0008_api_keys
Create Date: 2026-09-13
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0009_article_scores"
down_revision: Union[str, None] = "0008_api_keys"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("SET lock_timeout = '5s'")
    op.create_table(
        "article_scores",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("external_id", sa.String(length=160), nullable=False),
        sa.Column("headline", sa.Text(), nullable=False),
        sa.Column("score", sa.Numeric(6, 4), nullable=False),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("model_version", sa.String(length=64), nullable=False),
        sa.Column(
            "scored_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("external_id", name="uq_article_scores_external_id"),
    )
    op.create_index("ix_article_scores_external_id", "article_scores", ["external_id"])


def downgrade() -> None:
    op.execute("SET lock_timeout = '5s'")
    op.drop_index("ix_article_scores_external_id", table_name="article_scores")
    op.drop_table("article_scores")
