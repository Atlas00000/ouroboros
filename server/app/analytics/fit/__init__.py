"""Regime fit tags — map regimes onto MATCH / MISMATCH / FRAGILE per edge family."""

from app.analytics.fit.boards import board_from_ohlcv, board_from_regimes
from app.analytics.fit.entry_gate import EntryGateDecision, evaluate_entry_gate
from app.analytics.fit.gate import fit_from_regime_snapshot, live_fit
from app.analytics.fit.mapper import MODEL_VERSION, call_type_for_family, map_regime_to_fit
from app.analytics.fit.types import EDGE_FAMILIES, FIT_TAGS, EdgeFamily, FitSnapshot, FitTag

__all__ = [
    "EDGE_FAMILIES",
    "FIT_TAGS",
    "MODEL_VERSION",
    "EdgeFamily",
    "EntryGateDecision",
    "FitSnapshot",
    "FitTag",
    "board_from_ohlcv",
    "board_from_regimes",
    "call_type_for_family",
    "evaluate_entry_gate",
    "fit_from_regime_snapshot",
    "live_fit",
    "map_regime_to_fit",
]
