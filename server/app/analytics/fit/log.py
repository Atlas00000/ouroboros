"""Persist fit snapshots to forecast_log (call_type ``fit.{family}``)."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.analytics.bars import load_ohlcv, m1_depth_days
from app.analytics.fit.gate import DEFAULT_GATE_TIMEFRAMES, fit_from_regime_snapshot
from app.analytics.fit.mapper import MODEL_VERSION, call_type_for_family
from app.analytics.fit.types import EDGE_FAMILIES, EdgeFamily, FitSnapshot
from app.analytics.forecast_log import HORIZON_MINUTES
from app.analytics.metrics import Timeframe
from app.analytics.regimes import classify_regime
from app.calendar.timebase import ensure_utc
from app.models.asset import Asset
from app.models.forecast_log import ForecastLog


def fit_prediction_payload(snap: FitSnapshot) -> dict[str, Any]:
    return {
        "tag": snap.tag,
        "regime": snap.regime,
        "family": snap.family,
        "timeframe": snap.timeframe,
        "allow_on": snap.allow_on,
        "skipped": snap.skipped,
        "skip_reason": snap.skip_reason,
        "fragile_reasons": list(snap.fragile_reasons),
        "as_of": ensure_utc(snap.as_of).isoformat(),
    }


@dataclass(frozen=True)
class FitLogWriteResult:
    row: ForecastLog | None
    inserted: bool
    symbol: str
    timeframe: str
    call_type: str
    family: EdgeFamily


def log_fit_call(
    session: Session,
    snap: FitSnapshot,
    *,
    skip_duplicates: bool = True,
) -> FitLogWriteResult:
    """Append one fit nowcast to ``forecast_log`` (idempotent on unique key)."""
    sym = snap.symbol.upper()
    tf = str(snap.timeframe)
    call_type = call_type_for_family(snap.family)
    made_at = ensure_utc(snap.as_of)
    model_version = snap.model_version or MODEL_VERSION
    payload = fit_prediction_payload(snap)
    conf = round(float(min(1.0, max(0.0, snap.confidence))), 4)
    horizon = HORIZON_MINUTES.get(tf)

    if skip_duplicates:
        existing = session.scalar(
            select(ForecastLog).where(
                ForecastLog.symbol == sym,
                ForecastLog.timeframe == tf,
                ForecastLog.call_type == call_type,
                ForecastLog.made_at == made_at,
                ForecastLog.model_version == model_version,
            )
        )
        if existing is not None:
            return FitLogWriteResult(
                row=existing,
                inserted=False,
                symbol=sym,
                timeframe=tf,
                call_type=call_type,
                family=snap.family,
            )

        stmt = (
            pg_insert(ForecastLog)
            .values(
                symbol=sym,
                timeframe=tf,
                call_type=call_type,
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
                    ForecastLog.call_type == call_type,
                    ForecastLog.made_at == made_at,
                    ForecastLog.model_version == model_version,
                )
            )
            return FitLogWriteResult(
                row=existing,
                inserted=False,
                symbol=sym,
                timeframe=tf,
                call_type=call_type,
                family=snap.family,
            )
        row = session.get(ForecastLog, new_id)
        return FitLogWriteResult(
            row=row,
            inserted=True,
            symbol=sym,
            timeframe=tf,
            call_type=call_type,
            family=snap.family,
        )

    row = ForecastLog(
        symbol=sym,
        timeframe=tf,
        call_type=call_type,
        prediction_json=json.dumps(payload, separators=(",", ":")),
        model_version=model_version,
        confidence=conf,
        made_at=made_at,
        horizon_minutes=horizon,
    )
    session.add(row)
    session.flush()
    return FitLogWriteResult(
        row=row,
        inserted=True,
        symbol=sym,
        timeframe=tf,
        call_type=call_type,
        family=snap.family,
    )


@dataclass
class ClassifyAndLogFitReport:
    results: list[FitLogWriteResult] = field(default_factory=list)
    errors: list[tuple[str, str, str, str]] = field(default_factory=list)

    @property
    def inserted(self) -> int:
        return sum(1 for r in self.results if r.inserted)

    @property
    def skipped_dupes(self) -> int:
        return sum(1 for r in self.results if not r.inserted)


def classify_and_log_fits(
    session: Session,
    *,
    symbols: list[str] | None = None,
    families: tuple[EdgeFamily, ...] = EDGE_FAMILIES,
    timeframes: tuple[Timeframe, ...] = DEFAULT_GATE_TIMEFRAMES,
    lookback_days: int = 120,
    skip_duplicates: bool = True,
    commit: bool = True,
) -> ClassifyAndLogFitReport:
    """Classify regimes and append fit.* rows for each family × TF."""
    if symbols is None:
        symbols = [
            str(s)
            for s in session.scalars(select(Asset.symbol).where(Asset.is_active.is_(True))).all()
        ]

    report = ClassifyAndLogFitReport()
    for raw in symbols:
        sym = raw.upper()
        span = m1_depth_days(session, sym)
        for tf in timeframes:
            try:
                df = load_ohlcv(session, sym, tf, lookback_days=lookback_days)
                if df.empty:
                    report.errors.append((sym, tf, "-", "empty ohlcv"))
                    continue
                regime_snap = classify_regime(
                    df,
                    symbol=sym,
                    timeframe=tf,
                    m1_span_days_value=span,
                )
                for fam in families:
                    fit_snap = fit_from_regime_snapshot(regime_snap, fam)
                    result = log_fit_call(session, fit_snap, skip_duplicates=skip_duplicates)
                    report.results.append(result)
            except Exception as exc:  # noqa: BLE001
                report.errors.append((sym, tf, "-", str(exc)[:200]))
    if commit:
        session.commit()
    return report
