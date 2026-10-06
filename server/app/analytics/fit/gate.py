"""Live fit gate — nowcast tag + allow_on for research books."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.analytics.bars import load_ohlcv, m1_depth_days
from app.analytics.fit.mapper import MODEL_VERSION, map_regime_to_fit
from app.analytics.fit.types import EdgeFamily, FitSnapshot
from app.analytics.metrics import Timeframe
from app.analytics.regimes import RegimeSnapshot, classify_regime
from app.calendar.timebase import ensure_utc

DEFAULT_GATE_TIMEFRAMES: tuple[Timeframe, ...] = ("H1", "D1")
LOOKBACK_DAYS = 120


def fit_from_regime_snapshot(
    snap: RegimeSnapshot,
    family: EdgeFamily | str,
) -> FitSnapshot:
    """Map a regime snapshot to a fit snapshot (no I/O)."""
    fam: EdgeFamily
    if family not in ("meanrev", "trendfollow"):
        raise ValueError(f"unknown edge family: {family}")
    fam = family  # type: ignore[assignment]

    if snap.skipped:
        return FitSnapshot(
            symbol=snap.symbol.upper(),
            timeframe=str(snap.timeframe),
            family=fam,
            tag="MISMATCH",
            regime=None,
            model_version=MODEL_VERSION,
            as_of=ensure_utc(snap.as_of),
            allow_on=False,
            confidence=0.0,
            skipped=True,
            skip_reason=snap.skip_reason or "regime skipped",
            fragile_reasons=(),
        )

    tag = map_regime_to_fit(snap.regime, fam)
    fragile_reasons = ("high_volatility",) if snap.regime == "high_volatility" else ()
    conf = 0.0
    for p in snap.regime_probabilities:
        if p.regime == snap.regime:
            conf = float(min(1.0, max(0.0, p.probability)))
            break

    return FitSnapshot(
        symbol=snap.symbol.upper(),
        timeframe=str(snap.timeframe),
        family=fam,
        tag=tag,
        regime=snap.regime,
        model_version=MODEL_VERSION,
        as_of=ensure_utc(snap.as_of),
        allow_on=(tag == "MATCH"),
        confidence=conf,
        skipped=False,
        skip_reason=None,
        fragile_reasons=fragile_reasons,
    )


def live_fit(
    session: Session,
    symbol: str,
    timeframe: Timeframe | str,
    family: EdgeFamily | str,
    *,
    lookback_days: int = LOOKBACK_DAYS,
) -> FitSnapshot:
    """
    Classify latest regime and map to fit tag for ``family``.

    Research gate: ``allow_on`` is True only when tag == MATCH.
    """
    if family not in ("meanrev", "trendfollow"):
        raise ValueError(f"unknown edge family: {family}")
    fam: EdgeFamily = family  # type: ignore[assignment]
    sym = symbol.upper()
    tf = str(timeframe)
    df = load_ohlcv(session, sym, tf, lookback_days=lookback_days)  # type: ignore[arg-type]
    if df.empty:
        return FitSnapshot(
            symbol=sym,
            timeframe=tf,
            family=fam,
            tag="MISMATCH",
            regime=None,
            model_version=MODEL_VERSION,
            as_of=datetime.now(UTC),
            allow_on=False,
            confidence=0.0,
            skipped=True,
            skip_reason="empty ohlcv",
        )

    snap = classify_regime(
        df,
        symbol=sym,
        timeframe=tf,  # type: ignore[arg-type]
        m1_span_days_value=m1_depth_days(session, sym),
    )
    return fit_from_regime_snapshot(snap, fam)
