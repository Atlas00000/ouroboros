"""Daily AssetProfile builder — profile.v1 (Phase 2 W5·D1).

Assembles identity, volatility, liquidity proxies, correlations, and regime
distribution from deterministic analytics outputs. Persistence is W5·D2.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, time
from typing import Any

import pandas as pd
from contracts.common_v1 import Disclaimer, Provenance
from contracts.profile_v1 import (
    AssetIdentity,
    AssetProfile,
    CorrelationEntry,
    LiquidityCharacter,
    RegimeDistribution,
    TradingHours,
    VolatilityCharacter,
)

from app.analytics.correlations import CorrelationMatrixResult, compute_correlation_matrix
from app.analytics.metrics import (
    MODEL_VERSION as METRICS_MODEL_VERSION,
)
from app.analytics.metrics import (
    MetricSnapshot,
    compute_metric_snapshot,
)
from app.analytics.regimes import (
    DEFAULT_PARAMS,
    MODEL_VERSION as REGIME_MODEL_VERSION,
    REGIME_LABELS,
    RegimeParams,
    regime_feature_frame,
)
from app.analytics.universe import passes_depth_gate
from app.calendar.sessions import DEFAULT_SESSIONS, SessionName
from app.calendar.timebase import ensure_utc

PROFILE_MODEL_VERSION = "profiles.v1"


@dataclass(frozen=True)
class AssetIdentityInput:
    """Minimal identity fields (from DB ``assets`` row or tests)."""

    symbol: str
    display_name: str
    asset_class: str
    mt5_ticker: str | None = None
    base_currency: str | None = None
    quote_currency: str | None = None
    venues: tuple[str, ...] = ()


def _trading_hours_default(*, asset_class: str) -> TradingHours:
    sessions = [s.name.value for s in DEFAULT_SESSIONS]
    if asset_class == "fx":
        return TradingHours(
            timezone="UTC",
            sessions=sessions,
            open_utc=time(22, 0),
            close_utc=time(22, 0),
            notes="FX approx Sun 22:00–Fri 22:00 UTC; session names from calendar module.",
        )
    if asset_class == "metal":
        return TradingHours(
            timezone="UTC",
            sessions=sessions,
            notes="Metals follow broker session; gap-aware metrics applied.",
        )
    return TradingHours(
        timezone="UTC",
        sessions=[SessionName.NEW_YORK.value, SessionName.LONDON.value],
        notes="Index hours approximate; broker cash session may differ.",
    )


def regime_distribution_from_frame(
    features: pd.DataFrame,
    *,
    warmup_bars: int = 30,
) -> list[RegimeDistribution]:
    """Share of confirmed regime labels after warmup (sums to ~1 when any labels)."""
    if features.empty or "confirmed_regime" not in features.columns:
        return [RegimeDistribution(regime=r, share=0.0) for r in REGIME_LABELS]
    scored = features.iloc[max(warmup_bars, 0) :]
    labels = [str(x) for x in scored["confirmed_regime"].dropna().tolist()]
    total = len(labels) or 1
    counts = {r: 0 for r in REGIME_LABELS}
    for lab in labels:
        if lab in counts:
            counts[lab] += 1
    return [RegimeDistribution(regime=r, share=counts[r] / total) for r in REGIME_LABELS]


def correlations_for_symbol(
    matrix: CorrelationMatrixResult,
    symbol: str,
) -> list[CorrelationEntry]:
    """Pairwise entries involving ``symbol`` (other leg as ``symbol`` field)."""
    sym = symbol.upper()
    out: list[CorrelationEntry] = []
    for e in matrix.entries:
        if e.symbol_a == sym:
            out.append(
                CorrelationEntry(
                    symbol=e.symbol_b,
                    coefficient=e.coefficient,
                    window_days=e.window_days,
                )
            )
        elif e.symbol_b == sym:
            out.append(
                CorrelationEntry(
                    symbol=e.symbol_a,
                    coefficient=e.coefficient,
                    window_days=e.window_days,
                )
            )
    out.sort(key=lambda c: abs(c.coefficient), reverse=True)
    return out


def _confidence(
    *,
    d1_snap: MetricSnapshot | None,
    regime_dist: list[RegimeDistribution],
    m1_span: float,
    corr_count: int,
) -> float:
    score = 0.2
    if d1_snap is not None and d1_snap.atr_14 is not None:
        score += 0.25
    if d1_snap is not None and d1_snap.realized_vol_percentile_30d is not None:
        score += 0.2
    if any(d.share > 0 for d in regime_dist):
        score += 0.2
    if m1_span >= 90:
        score += 0.1
    if corr_count > 0:
        score += 0.05
    return float(min(score, 0.99))


def build_asset_profile(
    identity: AssetIdentityInput,
    *,
    d1_ohlcv: pd.DataFrame,
    h1_ohlcv: pd.DataFrame | None = None,
    peer_h1_ohlcv: dict[str, pd.DataFrame] | None = None,
    m1_span_by_symbol: dict[str, float] | None = None,
    profile_version: int = 1,
    as_of: datetime | None = None,
    regime_params: RegimeParams = DEFAULT_PARAMS,
    stale: bool = False,
) -> AssetProfile:
    """
    Build a ``profile.v1`` AssetProfile for one symbol.

    - Volatility / typical daily range from **D1** metrics
    - Liquidity: range percentile proxy; true spread deferred
    - Correlations: H1 30d matrix vs peers (depth-gated)
    - Regime distribution: confirmed labels on D1 (fallback H1) history
    """
    sym = identity.symbol.upper()
    spans = {k.upper(): float(v) for k, v in (m1_span_by_symbol or {}).items()}
    own_span = spans.get(sym, 0.0)

    d1_snap = (
        compute_metric_snapshot(d1_ohlcv, symbol=sym, timeframe="D1")
        if d1_ohlcv is not None and not d1_ohlcv.empty
        else None
    )
    as_of_dt = ensure_utc(as_of or (d1_snap.as_of if d1_snap else datetime.now(UTC)))

    # Prefer H1 for regime shares (denser labels); fall back to D1.
    regime_src: pd.DataFrame | None = None
    regime_tf: str | None = None
    if h1_ohlcv is not None and len(h1_ohlcv) >= 80:
        regime_src, regime_tf = h1_ohlcv, "H1"
    elif d1_ohlcv is not None and len(d1_ohlcv) >= 40:
        regime_src, regime_tf = d1_ohlcv, "D1"
    if (
        regime_src is not None
        and regime_tf is not None
        and passes_depth_gate(sym, m1_span_days_value=own_span)
    ):
        features = regime_feature_frame(regime_src, regime_tf, params=regime_params)  # type: ignore[arg-type]
        warmup = 30 if regime_tf == "D1" else 48
        regime_dist = regime_distribution_from_frame(features, warmup_bars=warmup)
    else:
        regime_dist = [RegimeDistribution(regime=r, share=0.0) for r in REGIME_LABELS]

    corr_entries: list[CorrelationEntry] = []
    if peer_h1_ohlcv:
        frames = {k.upper(): v for k, v in peer_h1_ohlcv.items() if v is not None and not v.empty}
        if h1_ohlcv is not None and not h1_ohlcv.empty:
            frames[sym] = h1_ohlcv
        if len(frames) >= 2:
            # Peers without explicit span default to deep enough to pass gate
            for s in frames:
                spans.setdefault(s, 400.0 if s != sym else own_span)
            spans[sym] = own_span
            matrix = compute_correlation_matrix(frames, m1_span_by_symbol=spans)
            corr_entries = correlations_for_symbol(matrix, sym)

    vol = VolatilityCharacter(
        atr_percentile_30d=d1_snap.atr_percentile_30d if d1_snap else None,
        realized_vol_percentile_30d=d1_snap.realized_vol_percentile_30d if d1_snap else None,
        typical_daily_range=d1_snap.range_mean_20 if d1_snap else None,
    )
    liq = LiquidityCharacter(
        typical_spread=None,
        spread_percentile_30d=d1_snap.range_percentile_30d if d1_snap else None,
        notes=(d1_snap.liquidity_note if d1_snap else "true bid/ask spread deferred"),
    )

    conf = _confidence(
        d1_snap=d1_snap,
        regime_dist=regime_dist,
        m1_span=own_span,
        corr_count=len(corr_entries),
    )

    return AssetProfile(
        profile_version=profile_version,
        identity=AssetIdentity(
            symbol=sym,
            display_name=identity.display_name,
            asset_class=identity.asset_class,
            venues=list(identity.venues),
            mt5_ticker=identity.mt5_ticker,
            base_currency=identity.base_currency,
            quote_currency=identity.quote_currency,
        ),
        trading_hours=_trading_hours_default(asset_class=identity.asset_class),
        volatility=vol,
        liquidity=liq,
        correlations=corr_entries,
        event_sensitivities=[],
        regime_distribution=regime_dist,
        as_of=as_of_dt,
        provenance=Provenance(
            sources=["mt5.prices", METRICS_MODEL_VERSION, REGIME_MODEL_VERSION],
            generated_at=datetime.now(UTC),
            model_version=PROFILE_MODEL_VERSION,
            confidence=conf,
            stale=stale,
        ),
        disclaimer=Disclaimer(),
    )


def build_asset_profile_from_session(
    session: Any,
    symbol: str,
    *,
    profile_version: int = 1,
    lookback_days: int = 120,
    peer_symbols: list[str] | None = None,
) -> AssetProfile:
    """Load OHLCV + asset row from DB and build a profile (W5·D1 orchestration)."""
    from sqlalchemy import select

    from app.analytics.bars import load_ohlcv, m1_depth_days
    from app.models.asset import Asset

    sym = symbol.upper()
    row = session.scalar(select(Asset).where(Asset.symbol == sym))
    if row is None:
        raise KeyError(f"unknown asset: {sym}")

    venues: tuple[str, ...] = ()
    if row.venues:
        venues = tuple(v.strip() for v in str(row.venues).split(",") if v.strip())

    identity = AssetIdentityInput(
        symbol=row.symbol,
        display_name=row.display_name,
        asset_class=row.asset_class,
        mt5_ticker=row.mt5_ticker,
        base_currency=row.base_currency,
        quote_currency=row.quote_currency,
        venues=venues,
    )

    d1 = load_ohlcv(session, sym, "D1", lookback_days=lookback_days)
    h1 = load_ohlcv(session, sym, "H1", lookback_days=max(lookback_days, 45))
    span = m1_depth_days(session, sym)

    peers = peer_symbols
    if peers is None:
        peers = [
            str(s)
            for s in session.scalars(select(Asset.symbol).where(Asset.is_active.is_(True))).all()
        ]

    peer_frames: dict[str, pd.DataFrame] = {}
    span_map: dict[str, float] = {sym: span}
    for p in peers:
        p_up = str(p).upper()
        peer_frames[p_up] = load_ohlcv(session, p_up, "H1", lookback_days=max(lookback_days, 45))
        span_map[p_up] = m1_depth_days(session, p_up)

    return build_asset_profile(
        identity,
        d1_ohlcv=d1,
        h1_ohlcv=h1,
        peer_h1_ohlcv=peer_frames,
        m1_span_by_symbol=span_map,
        profile_version=profile_version,
    )
