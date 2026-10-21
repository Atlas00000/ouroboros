"""map equity/energy/index mt5_tickers to YWO-Trade Market Watch names

Revision ID: 0014_ywo_equity_tickers
Revises: 0013_seed_extra_indices
Create Date: 2026-10-07

Canonical symbols stay AAPL / XTIUSD / DE40 etc. for news/calendar mapping.
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op

revision: str = "0014_ywo_equity_tickers"
down_revision: Union[str, None] = "0013_seed_extra_indices"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Verified against YWO-Trade terminal (2026-10-07).
FORWARD = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "AMZN": "Amazon",
    "META": "Meta",
    "GOOGL": "Alphabet",
    "TSLA": "Tesla",
    "JPM": "JPMorgan",
    "AVGO": "Broadcom",
    "XOM": "Exxon",
    # NVDA already resolves as NVDA
    "XTIUSD": "WTI",
    "XBRUSD": "BRENT",
    "DE40": "DE30",  # YWO still lists DE30 for Germany cash CFD
    "JP225": "JPN225",
}

REVERSE = {
    "AAPL": "AAPL",
    "MSFT": "MSFT",
    "AMZN": "AMZN",
    "META": "META",
    "GOOGL": "GOOGL",
    "TSLA": "TSLA",
    "JPM": "JPM",
    "AVGO": "AVGO",
    "XOM": "XOM",
    "XTIUSD": "XTIUSD",
    "XBRUSD": "XBRUSD",
    "DE40": "GER40",
    "JP225": "JP225",
}


def upgrade() -> None:
    op.execute("SET lock_timeout = '5s'")
    for symbol, ticker in FORWARD.items():
        op.execute(f"UPDATE assets SET mt5_ticker = '{ticker}' WHERE symbol = '{symbol}'")


def downgrade() -> None:
    op.execute("SET lock_timeout = '5s'")
    for symbol, ticker in REVERSE.items():
        op.execute(f"UPDATE assets SET mt5_ticker = '{ticker}' WHERE symbol = '{symbol}'")
