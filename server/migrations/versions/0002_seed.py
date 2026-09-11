"""seed asset universe and source registry

Revision ID: 0002_seed
Revises: 0001_initial
Create Date: 2026-09-11
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002_seed"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Major FX + metals + indices — MVP universe (roadmap decision #8)
ASSETS = [
    ("EURUSD", "Euro / US Dollar", "fx", "EURUSD", "EUR", "USD"),
    ("GBPUSD", "British Pound / US Dollar", "fx", "GBPUSD", "GBP", "USD"),
    ("USDJPY", "US Dollar / Japanese Yen", "fx", "USDJPY", "USD", "JPY"),
    ("USDCHF", "US Dollar / Swiss Franc", "fx", "USDCHF", "USD", "CHF"),
    ("AUDUSD", "Australian Dollar / US Dollar", "fx", "AUDUSD", "AUD", "USD"),
    ("USDCAD", "US Dollar / Canadian Dollar", "fx", "USDCAD", "USD", "CAD"),
    ("NZDUSD", "New Zealand Dollar / US Dollar", "fx", "NZDUSD", "NZD", "USD"),
    ("EURGBP", "Euro / British Pound", "fx", "EURGBP", "EUR", "GBP"),
    ("EURJPY", "Euro / Japanese Yen", "fx", "EURJPY", "EUR", "JPY"),
    ("GBPJPY", "British Pound / Japanese Yen", "fx", "GBPJPY", "GBP", "JPY"),
    ("XAUUSD", "Gold / US Dollar", "metal", "XAUUSD", "XAU", "USD"),
    ("XAGUSD", "Silver / US Dollar", "metal", "XAGUSD", "XAG", "USD"),
    ("US500", "S&P 500", "index", "US500", None, "USD"),
    ("US30", "Dow Jones Industrial Average", "index", "US30", None, "USD"),
    ("NAS100", "Nasdaq 100", "index", "NAS100", None, "USD"),
]

SOURCES = [
    ("mt5.prices", "MetaTrader 5 prices", "price", 60, "Derived bars for internal platforms only."),
    ("finnhub.news", "Finnhub news", "news", 60, "Confirm redistribution / derived-data terms."),
    ("finnhub.calendar", "Finnhub economic calendar", "calendar", 300, "Confirm redistribution terms."),
    ("fred.macro", "FRED macro series", "macro", 86400, "Public domain / FRED terms of use."),
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
            for s, name, klass, mt5, base, quote in ASSETS
        ],
    )

    sources = sa.table(
        "source_registry",
        sa.column("source_id", sa.String),
        sa.column("name", sa.String),
        sa.column("kind", sa.String),
        sa.column("expected_cadence_seconds", sa.Integer),
        sa.column("status", sa.String),
        sa.column("license_notes", sa.String),
    )
    op.bulk_insert(
        sources,
        [
            {
                "source_id": sid,
                "name": name,
                "kind": kind,
                "expected_cadence_seconds": cadence,
                "status": "pending",
                "license_notes": license_notes,
            }
            for sid, name, kind, cadence, license_notes in SOURCES
        ],
    )


def downgrade() -> None:
    op.execute("SET lock_timeout = '5s'")
    symbols = ", ".join(f"'{s[0]}'" for s in ASSETS)
    source_ids = ", ".join(f"'{s[0]}'" for s in SOURCES)
    op.execute(f"DELETE FROM source_registry WHERE source_id IN ({source_ids})")
    op.execute(f"DELETE FROM assets WHERE symbol IN ({symbols})")
