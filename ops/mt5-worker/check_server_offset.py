"""Saturday-safe MT5 server-time offset check.

Compares:
1) live MT5 terminal server time vs wall UTC
2) last stored prices.ts (UTC) vs what MT5 reports for that bar if available
"""

from __future__ import annotations

import os
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

SERVER_ROOT = Path(__file__).resolve().parents[2] / "server"
sys.path.insert(0, str(SERVER_ROOT))
os.chdir(SERVER_ROOT)

from sqlalchemy import text

from app.config import get_settings
from app.calendar.timebase import infer_mt5_offset_hours
from app.db.session import get_session_factory
from app.ingestion.mt5.connection import connect, disconnect, _import_mt5


def main() -> int:
    get_settings.cache_clear()
    settings = get_settings()
    now_utc = datetime.now(UTC)
    inferred = infer_mt5_offset_hours(now_utc)
    configured = float(settings.mt5_server_utc_offset_hours)
    buch = now_utc.astimezone(ZoneInfo("Europe/Bucharest"))

    print("=== clocks (works on Saturday) ===")
    print(f"wall_utc              {now_utc.isoformat()}")
    print(f"europe/bucharest      {buch.isoformat()}")
    print(f"inferred_offset_h     {inferred}")
    print(f"configured_offset_h   {configured}  (MT5_SERVER_UTC_OFFSET_HOURS)")
    print(f"expected_server_clock {buch.strftime('%Y-%m-%d %H:%M:%S')}  << compare to MT5 Market Watch / terminal clock")

    print("\n=== last Friday tip in DB (UTC) ===")
    session = get_session_factory()()
    try:
        row = session.execute(
            text(
                "SELECT symbol, ts FROM prices WHERE symbol='EURUSD' "
                "ORDER BY ts DESC LIMIT 1"
            )
        ).one()
        print(f"EURUSD last bar UTC  {row.ts}")
        print(f"  + configured offset -> server-like {row.ts.astimezone(UTC) + timedelta(hours=configured)}")
        print(f"  + inferred offset   -> server-like {row.ts.astimezone(UTC) + timedelta(hours=inferred)}")
    finally:
        session.close()

    print("\n=== live MT5 terminal_info / tick (if terminal is open) ===")
    try:
        connect(settings)
        mt5 = _import_mt5()
        ti = mt5.terminal_info()
        ai = mt5.account_info()
        tick = mt5.symbol_info_tick("EURUSD")
        print(f"connected login={getattr(ai, 'login', None)} server={getattr(ai, 'server', None)}")
        # MetaTrader5 exposes time as unix seconds in tick.time (server time epoch)
        if tick is not None and getattr(tick, "time", 0):
            tick_server = datetime.fromtimestamp(tick.time, tz=UTC)
            # tick.time is typically broker/server local expressed as naive epoch — treat carefully
            print(f"EURUSD tick.time raw epoch {tick.time}")
            print(f"  as UTC wall from epoch   {tick_server.isoformat()}")
            delta_h = (tick_server - now_utc).total_seconds() / 3600.0
            print(f"  epoch_vs_wall_utc_hours  {delta_h:.3f}  (often ~0 if terminal stores UTC epoch)")
        # Also print server time via copy_rates_from_pos last bar time
        rates = mt5.copy_rates_from_pos("EURUSD", mt5.TIMEFRAME_M1, 0, 1)
        if rates is not None and len(rates):
            bar_epoch = int(rates[0]["time"])
            bar_as_utc = datetime.fromtimestamp(bar_epoch, tz=UTC)
            print(f"last M1 bar epoch          {bar_epoch} -> {bar_as_utc.isoformat()} (if broker uses UTC epoch this is true UTC)")
            print(f"DB last EURUSD should be near that bar when markets last printed")
        disconnect()
    except Exception as exc:  # noqa: BLE001
        print(f"MT5 probe skipped/failed: {exc}")
        print("Open MetaTrader 5 (logged into YWO-Trade), then re-run this script.")
        return 1

    print("\n=== how to confirm visually ===")
    print("1. Look at the clock in the MT5 terminal status bar / Market Watch header.")
    print("2. It should match 'expected_server_clock' above (±1–2 minutes).")
    print("3. If MT5 shows ~1h ahead/behind that, set MT5_SERVER_UTC_OFFSET_HOURS accordingly.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
