"""seed DE40 / UK100 / JP225 indices

Revision ID: 0013_seed_extra_indices
Revises: 0012_seed_materials
Create Date: 2026-10-07
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0013_seed_extra_indices"
down_revision: Union[str, None] = "0012_seed_materials"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# mt5_ticker = YWO Market Watch names (DE30 is YWO's Germany cash CFD).
INDICES = [
    ("DE40", "Germany 40 (DAX)", "index", "DE30", None, "EUR"),
    ("UK100", "UK 100 (FTSE)", "index", "UK100", None, "GBP"),
    ("JP225", "Japan 225 (Nikkei)", "index", "JPN225", None, "JPY"),
]


def upgrade() -> None:
    op.execute("SET lock_timeout = '5s'")
    assets = sa.table(
        "assets",
        sa.column("symbol", sa.String),
        sa.column("display_name", sa.String),
        sa.column("asset_class", sa.String),
        sa.column("mt5_ticker", sa.String),
        sa.column("base_currency", sa.String),
        sa.column("quote_currency", sa.String),
        sa.column("is_active", sa.Boolean),
    )
    op.bulk_insert(
        assets,
        [
            {
                "symbol": s,
                "display_name": name,
                "asset_class": klass,
                "mt5_ticker": mt5,
                "base_currency": base,
                "quote_currency": quote,
                "is_active": True,
            }
            for s, name, klass, mt5, base, quote in INDICES
        ],
    )


def downgrade() -> None:
    op.execute("SET lock_timeout = '5s'")
    symbols = ", ".join(f"'{s[0]}'" for s in INDICES)
    op.execute(f"DELETE FROM assets WHERE symbol IN ({symbols})")
