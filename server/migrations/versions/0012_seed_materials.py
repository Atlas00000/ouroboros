"""seed energy materials (WTI / Brent)

Revision ID: 0012_seed_materials
Revises: 0011_seed_equities
Create Date: 2026-10-07
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0012_seed_materials"
down_revision: Union[str, None] = "0011_seed_equities"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# asset_class stays metal (contract has no commodity); display names mark energy.
MATERIALS = [
    ("XTIUSD", "WTI Crude Oil", "metal", "WTI", "XTI", "USD"),
    ("XBRUSD", "Brent Crude Oil", "metal", "BRENT", "XBR", "USD"),
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
            for s, name, klass, mt5, base, quote in MATERIALS
        ],
    )


def downgrade() -> None:
    op.execute("SET lock_timeout = '5s'")
    symbols = ", ".join(f"'{s[0]}'" for s in MATERIALS)
    op.execute(f"DELETE FROM assets WHERE symbol IN ({symbols})")
