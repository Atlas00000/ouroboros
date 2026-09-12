"""MT5 ingestion package."""

from app.ingestion.mt5.backfill import BackfillResult, backfill_symbol, backfill_universe
from app.ingestion.mt5.connection import Mt5ConnectionInfo, connect, disconnect, ensure_connected
from app.ingestion.mt5.poller import GapWindow, SymbolPollResult, poll_once, poll_symbol, run_poll_loop
from app.ingestion.mt5.rates import RawBar, fetch_m1_range, probe_rates
from app.ingestion.mt5.symbols import SymbolMapEntry, SymbolMapper

__all__ = [
    "BackfillResult",
    "GapWindow",
    "Mt5ConnectionInfo",
    "RawBar",
    "SymbolMapEntry",
    "SymbolMapper",
    "SymbolPollResult",
    "backfill_symbol",
    "backfill_universe",
    "connect",
    "disconnect",
    "ensure_connected",
    "fetch_m1_range",
    "poll_once",
    "poll_symbol",
    "probe_rates",
    "run_poll_loop",
]
