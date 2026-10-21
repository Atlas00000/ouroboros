"""Verify assets.mt5_ticker resolve in the connected MT5 terminal."""

from __future__ import annotations

import os
import sys
from pathlib import Path

SERVER_ROOT = Path(__file__).resolve().parents[2] / "server"
sys.path.insert(0, str(SERVER_ROOT))
os.chdir(SERVER_ROOT)

from sqlalchemy import select  # noqa: E402

from app.config import get_settings  # noqa: E402
from app.db.session import get_session_factory  # noqa: E402
from app.ingestion.mt5.connection import connect, disconnect  # noqa: E402
from app.models.asset import Asset  # noqa: E402


def main() -> int:
    get_settings.cache_clear()
    settings = get_settings()
    info = connect(settings)
    if not info.connected:
        print(f"FAILED login: {info.error}")
        return 1

    import MetaTrader5 as mt5

    session = get_session_factory()()
    try:
        rows = session.scalars(select(Asset).where(Asset.is_active.is_(True))).all()
        missing: list[str] = []
        for row in rows:
            ticker = (row.mt5_ticker or row.symbol).strip()
            selected = mt5.symbol_select(ticker, True)
            si = mt5.symbol_info(ticker) if selected else None
            status = "OK" if si is not None else "MISSING"
            if si is None:
                missing.append(f"{row.symbol}->{ticker}")
            print(f"{row.symbol:8} class={row.asset_class:6} ticker={ticker:12} {status}")
    finally:
        session.close()
        disconnect()

    if missing:
        print(f"MISSING {len(missing)}: {', '.join(missing)}")
        return 1
    print("all tickers resolve")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
