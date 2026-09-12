"""map index mt5_tickers to YWO-Trade names

Revision ID: 0004_ywo_index_tickers
Revises: 0003_macro
Create Date: 2026-09-12

YWO-Trade Market Watch uses SPX500 / US100 instead of US500 / NAS100.
Canonical symbols stay US500 / NAS100 for news/calendar mapping.
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op

revision: str = "0004_ywo_index_tickers"
down_revision: Union[str, None] = "0003_macro"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("SET lock_timeout = '5s'")
    op.execute("UPDATE assets SET mt5_ticker = 'SPX500' WHERE symbol = 'US500'")
    op.execute("UPDATE assets SET mt5_ticker = 'US100' WHERE symbol = 'NAS100'")
    # US30 already matches YWO-Trade


def downgrade() -> None:
    op.execute("SET lock_timeout = '5s'")
    op.execute("UPDATE assets SET mt5_ticker = 'US500' WHERE symbol = 'US500'")
    op.execute("UPDATE assets SET mt5_ticker = 'NAS100' WHERE symbol = 'NAS100'")
