"""Symbol mapper unit tests."""

from __future__ import annotations

import pytest

from app.ingestion.mt5.symbols import SymbolMapEntry, SymbolMapper


def test_symbol_mapper_roundtrip() -> None:
    mapper = SymbolMapper(
        [
            SymbolMapEntry("EURUSD", "EURUSD", "fx", True),
            SymbolMapEntry("XAUUSD", "GOLD", "metal", True),
        ]
    )
    assert mapper.to_mt5("EURUSD") == "EURUSD"
    assert mapper.to_mt5("xauusd") == "GOLD"
    assert mapper.to_canonical("GOLD") == "XAUUSD"
    assert len(mapper) == 2


def test_symbol_mapper_unknown() -> None:
    mapper = SymbolMapper([])
    with pytest.raises(KeyError):
        mapper.to_mt5("EURUSD")
