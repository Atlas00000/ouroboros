"""seed 10 liquid US equities

Revision ID: 0011_seed_equities
Revises: 0010_scoring_weekly
Create Date: 2026-10-07
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0011_seed_equities"
down_revision: Union[str, None] = "0010_scoring_weekly"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Canonical = ticker; mt5_ticker = YWO Market Watch name (see also 0014).
EQUITIES = [
    ("AAPL", "Apple Inc.", "equity", "Apple", None, "USD"),
    ("MSFT", "Microsoft Corporation", "equity", "Microsoft", None, "USD"),
    ("NVDA", "NVIDIA Corporation", "equity", "NVDA", None, "USD"),
    ("AMZN", "Amazon.com Inc.", "equity", "Amazon", None, "USD"),
    ("META", "Meta Platforms Inc.", "equity", "Meta", None, "USD"),
    ("GOOGL", "Alphabet Inc. Class A", "equity", "Alphabet", None, "USD"),
    ("TSLA", "Tesla Inc.", "equity", "Tesla", None, "USD"),
    ("JPM", "JPMorgan Chase & Co.", "equity", "JPMorgan", None, "USD"),
    ("AVGO", "Broadcom Inc.", "equity", "Broadcom", None, "USD"),
    ("XOM", "Exxon Mobil Corporation", "equity", "Exxon", None, "USD"),
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
            for s, name, klass, mt5, base, quote in EQUITIES
        ],
    )


def downgrade() -> None:
    op.execute("SET lock_timeout = '5s'")
    symbols = ", ".join(f"'{s[0]}'" for s in EQUITIES)
    op.execute(f"DELETE FROM assets WHERE symbol IN ({symbols})")
