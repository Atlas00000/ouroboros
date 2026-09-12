"""Canonical symbol ↔ MT5 ticker mapping."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.asset import Asset


@dataclass(frozen=True)
class SymbolMapEntry:
    symbol: str
    mt5_ticker: str
    asset_class: str
    is_active: bool


class SymbolMapper:
    """Loads asset rows and resolves MT5 tickers (fallback: ticker == symbol)."""

    def __init__(self, entries: list[SymbolMapEntry]) -> None:
        self._by_symbol = {e.symbol.upper(): e for e in entries}
        self._by_mt5 = {e.mt5_ticker.upper(): e for e in entries}

    @classmethod
    def from_session(cls, session: Session, *, active_only: bool = True) -> SymbolMapper:
        stmt = select(Asset)
        if active_only:
            stmt = stmt.where(Asset.is_active.is_(True))
        rows = session.scalars(stmt).all()
        entries = [
            SymbolMapEntry(
                symbol=row.symbol,
                mt5_ticker=(row.mt5_ticker or row.symbol),
                asset_class=row.asset_class,
                is_active=row.is_active,
            )
            for row in rows
        ]
        return cls(entries)

    def to_mt5(self, symbol: str) -> str:
        entry = self._by_symbol.get(symbol.upper())
        if entry is None:
            raise KeyError(f"Unknown canonical symbol: {symbol}")
        return entry.mt5_ticker

    def to_canonical(self, mt5_ticker: str) -> str:
        entry = self._by_mt5.get(mt5_ticker.upper())
        if entry is None:
            raise KeyError(f"Unknown MT5 ticker: {mt5_ticker}")
        return entry.symbol

    def all_mt5_tickers(self) -> list[str]:
        return [e.mt5_ticker for e in self._by_symbol.values()]

    def all_symbols(self) -> list[str]:
        return list(self._by_symbol.keys())

    def __len__(self) -> int:
        return len(self._by_symbol)
