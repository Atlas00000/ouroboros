"""Immutable forecast / regime-call log writer (Phase 2 W5·D3).

Append-only: prediction fields are never updated after insert. Scoring jobs
(W8) may fill ``realized_json`` / ``scored_at`` / ``score`` only.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any, Literal

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.analytics.bars import load_ohlcv, m1_depth_days
from app.analytics.metrics import Timeframe
from app.analytics.regimes import MODEL_VERSION as REGIME_MODEL_VERSION
from app.analytics.regimes import RegimeSnapshot, classify_regime
from app.calendar.timebase import ensure_utc
from app.models.asset import Asset
from app.models.forecast_log import ForecastLog

CallType = Literal["regime", "forecast"]

# Default evaluation horizon for scoring (bar length in minutes).
HORIZON_MINUTES: dict[str, int] = {
    "M1": 1,
    "M15": 15,
    "H1": 60,
    "H4": 240,
    "D1": 1440,
}

DEFAULT_LOG_TIMEFRAMES: tuple[Timeframe, ...] = ("H1", "H4", "D1")


def regime_prediction_payload(snap: RegimeSnapshot) -> dict[str, Any]:
    """JSON-serializable prediction body for a regime call."""
    return {
        "regime": snap.regime,
        "raw_regime": snap.raw_regime,
        "probabilities": [
            {"regime": p.regime, "probability": float(p.probability)}
            for p in snap.regime_probabilities
        ],
        "volatility_percentile": snap.volatility_percentile,
        "trend_strength": snap.trend_strength,
        "skipped": bool(snap.skipped),
        "skip_reason": snap.skip_reason,
        "as_of": ensure_utc(snap.as_of).isoformat(),
    }


def confidence_from_snapshot(snap: RegimeSnapshot) -> float:
    """Use soft-prob mass on the confirmed regime; 0 when skipped."""
    if snap.skipped:
        return 0.0
    for p in snap.regime_probabilities:
        if p.regime == snap.regime:
            return float(min(1.0, max(0.0, p.probability)))
    return 0.5


@dataclass(frozen=True)
class LogWriteResult:
    row: ForecastLog | None
    inserted: bool
    symbol: str
    timeframe: str
    call_type: CallType


def _to_confidence(value: float) -> Decimal:
    return Decimal(str(round(float(value), 4)))


def log_regime_call(
    session: Session,
    snap: RegimeSnapshot,
    *,
    skip_duplicates: bool = True,
) -> LogWriteResult:
    """
    Append one regime classification to ``forecast_log``.

    Idempotent on (symbol, timeframe, call_type, made_at, model_version) when
    ``skip_duplicates`` is True (migration 0007 unique index).
    """
    sym = snap.symbol.upper()
    tf = str(snap.timeframe)
    made_at = ensure_utc(snap.as_of)
    model_version = snap.model_version or REGIME_MODEL_VERSION
    payload = regime_prediction_payload(snap)
    conf = _to_confidence(confidence_from_snapshot(snap))
    horizon = HORIZON_MINUTES.get(tf)

    if skip_duplicates:
        existing = session.scalar(
            select(ForecastLog).where(
                ForecastLog.symbol == sym,
                ForecastLog.timeframe == tf,
                ForecastLog.call_type == "regime",
                ForecastLog.made_at == made_at,
                ForecastLog.model_version == model_version,
            )
        )
        if existing is not None:
            return LogWriteResult(
                row=existing,
                inserted=False,
                symbol=sym,
                timeframe=tf,
                call_type="regime",
            )

        stmt = (
            pg_insert(ForecastLog)
            .values(
                symbol=sym,
                timeframe=tf,
                call_type="regime",
                prediction_json=json.dumps(payload, separators=(",", ":")),
                model_version=model_version,
                confidence=conf,
                made_at=made_at,
                horizon_minutes=horizon,
            )
            .on_conflict_do_nothing(
                index_elements=[
                    "symbol",
                    "timeframe",
                    "call_type",
                    "made_at",
                    "model_version",
                ]
            )
            .returning(ForecastLog.id)
        )
        new_id = session.scalar(stmt)
        session.flush()
        if new_id is None:
            existing = session.scalar(
                select(ForecastLog).where(
                    ForecastLog.symbol == sym,
                    ForecastLog.timeframe == tf,
                    ForecastLog.call_type == "regime",
                    ForecastLog.made_at == made_at,
                    ForecastLog.model_version == model_version,
                )
            )
            return LogWriteResult(
                row=existing,
                inserted=False,
                symbol=sym,
                timeframe=tf,
                call_type="regime",
            )
        row = session.get(ForecastLog, new_id)
        return LogWriteResult(
            row=row,
            inserted=True,
            symbol=sym,
            timeframe=tf,
            call_type="regime",
        )

    row = ForecastLog(
        symbol=sym,
        timeframe=tf,
        call_type="regime",
        prediction_json=json.dumps(payload, separators=(",", ":")),
        model_version=model_version,
        confidence=conf,
        made_at=made_at,
        horizon_minutes=horizon,
    )
    session.add(row)
    session.flush()
    return LogWriteResult(
        row=row,
        inserted=True,
        symbol=sym,
        timeframe=tf,
        call_type="regime",
    )


def log_forecast_call(
    session: Session,
    *,
    symbol: str,
    timeframe: str,
    prediction: dict[str, Any],
    model_version: str,
    confidence: float,
    made_at: datetime,
    horizon_minutes: int | None = None,
    skip_duplicates: bool = True,
) -> LogWriteResult:
    """Append a generic forecast call (non-regime) for future scorers."""
    sym = symbol.upper()
    tf = str(timeframe)
    made = ensure_utc(made_at)
    conf = _to_confidence(confidence)
    horizon = horizon_minutes if horizon_minutes is not None else HORIZON_MINUTES.get(tf)
    payload_json = json.dumps(prediction, separators=(",", ":"), default=str)

    if skip_duplicates:
        existing = session.scalar(
            select(ForecastLog).where(
                ForecastLog.symbol == sym,
                ForecastLog.timeframe == tf,
                ForecastLog.call_type == "forecast",
                ForecastLog.made_at == made,
                ForecastLog.model_version == model_version,
            )
        )
        if existing is not None:
            return LogWriteResult(
                row=existing,
                inserted=False,
                symbol=sym,
                timeframe=tf,
                call_type="forecast",
            )

    row = ForecastLog(
        symbol=sym,
        timeframe=tf,
        call_type="forecast",
        prediction_json=payload_json,
        model_version=model_version,
        confidence=conf,
        made_at=made,
        horizon_minutes=horizon,
    )
    session.add(row)
    session.flush()
    return LogWriteResult(
        row=row,
        inserted=True,
        symbol=sym,
        timeframe=tf,
        call_type="forecast",
    )


@dataclass
class ClassifyAndLogReport:
    results: list[LogWriteResult]
    errors: list[tuple[str, str, str]]  # symbol, tf, error

    @property
    def inserted(self) -> int:
        return sum(1 for r in self.results if r.inserted)

    @property
    def skipped_dupes(self) -> int:
        return sum(1 for r in self.results if not r.inserted)


def classify_and_log_regimes(
    session: Session,
    *,
    symbols: list[str] | None = None,
    timeframes: tuple[Timeframe, ...] = DEFAULT_LOG_TIMEFRAMES,
    lookback_days: int = 120,
    skip_duplicates: bool = True,
    commit: bool = True,
) -> ClassifyAndLogReport:
    """
    Classify latest bar for each symbol/TF and append to ``forecast_log``.

    Skipped depth-gate classifications are still recorded (audit + model_version).
    """
    if symbols is None:
        symbols = [
            str(s)
            for s in session.scalars(select(Asset.symbol).where(Asset.is_active.is_(True))).all()
        ]

    report = ClassifyAndLogReport(results=[], errors=[])
    for raw in symbols:
        sym = raw.upper()
        span = m1_depth_days(session, sym)
        for tf in timeframes:
            try:
                df = load_ohlcv(session, sym, tf, lookback_days=lookback_days)
                if df.empty:
                    report.errors.append((sym, tf, "empty ohlcv"))
                    continue
                snap = classify_regime(
                    df,
                    symbol=sym,
                    timeframe=tf,
                    m1_span_days_value=span,
                )
                result = log_regime_call(session, snap, skip_duplicates=skip_duplicates)
                report.results.append(result)
            except Exception as exc:  # noqa: BLE001 — per-symbol continue
                report.errors.append((sym, tf, str(exc)[:200]))
    if commit:
        session.commit()
    return report
