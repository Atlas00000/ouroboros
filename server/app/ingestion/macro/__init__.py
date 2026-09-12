"""Macro ingestion package (FRED)."""

from app.ingestion.macro.client import FredClient, RawMacroPoint
from app.ingestion.macro.poller import MacroPollResult, poll_once
from app.ingestion.macro.writer import upsert_macro_points

__all__ = [
    "FredClient",
    "MacroPollResult",
    "RawMacroPoint",
    "poll_once",
    "upsert_macro_points",
]
