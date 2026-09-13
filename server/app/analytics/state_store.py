"""Persist MarketState (state.v1) + regime.changed outbox (W6·D2/D3)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from contracts.common_v1 import Disclaimer, Provenance
from contracts.events_v1 import RegimeChangedEvent, RegimeChangedPayload
from contracts.state_v1 import MarketState, RegimeProbability
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analytics.regimes import MODEL_VERSION as REGIME_MODEL_VERSION
from app.analytics.regimes import RegimeSnapshot
from app.calendar.timebase import ensure_utc
from app.models.outbox import OutboxMessage
from app.models.state import MarketStateRow


def confidence_from_snapshot(snap: RegimeSnapshot) -> float:
    if snap.skipped:
        return 0.0
    for p in snap.regime_probabilities:
        if p.regime == snap.regime:
            return float(min(1.0, max(0.0, p.probability)))
    return 0.5


def market_state_from_snapshot(snap: RegimeSnapshot) -> MarketState:
    now = datetime.now(UTC)
    return MarketState(
        symbol=snap.symbol.upper(),
        timeframe=snap.timeframe,
        regime=snap.regime,
        regime_probabilities=[
            RegimeProbability(regime=p.regime, probability=float(p.probability))
            for p in snap.regime_probabilities
        ],
        volatility_percentile=snap.volatility_percentile,
        trend_strength=snap.trend_strength,
        as_of=ensure_utc(snap.as_of),
        provenance=Provenance(
            sources=["mt5.prices", snap.model_version or REGIME_MODEL_VERSION],
            generated_at=now,
            model_version=snap.model_version or REGIME_MODEL_VERSION,
            confidence=confidence_from_snapshot(snap),
            stale=bool(snap.skipped),
        ),
        disclaimer=Disclaimer(),
    )


def market_state_from_row(row: MarketStateRow) -> MarketState:
    probs = json.loads(row.probabilities_json)
    return MarketState(
        symbol=row.symbol,
        timeframe=row.timeframe,  # type: ignore[arg-type]
        regime=row.regime,  # type: ignore[arg-type]
        regime_probabilities=[RegimeProbability(**p) for p in probs],
        volatility_percentile=float(row.volatility_percentile)
        if row.volatility_percentile is not None
        else None,
        trend_strength=float(row.trend_strength) if row.trend_strength is not None else None,
        as_of=ensure_utc(row.as_of),
        provenance=Provenance(
            sources=json.loads(row.sources_json) if row.sources_json else [row.model_version],
            generated_at=ensure_utc(row.created_at),
            model_version=row.model_version,
            confidence=float(row.confidence),
            stale=bool(row.stale),
        ),
        disclaimer=Disclaimer(),
    )


def latest_state_row(
    session: Session,
    symbol: str,
    timeframe: str,
) -> MarketStateRow | None:
    sym = symbol.upper()
    return session.scalar(
        select(MarketStateRow)
        .where(MarketStateRow.symbol == sym, MarketStateRow.timeframe == timeframe)
        .order_by(MarketStateRow.as_of.desc(), MarketStateRow.id.desc())
        .limit(1)
    )


@dataclass(frozen=True)
class StatePersistResult:
    row: MarketStateRow
    changed: bool
    outbox_event_id: str | None


def persist_regime_state(
    session: Session,
    snap: RegimeSnapshot,
    *,
    enqueue_outbox: bool = True,
) -> StatePersistResult | None:
    """
    Insert a state row when regime differs from latest (or first write).

    Skipped classifications are not persisted. Emits ``regime.changed`` outbox
    in the same session when the confirmed regime flips.
    """
    if snap.skipped:
        return None

    sym = snap.symbol.upper()
    tf = str(snap.timeframe)
    prev_row = latest_state_row(session, sym, tf)
    previous_regime = prev_row.regime if prev_row is not None else None
    changed = previous_regime is None or previous_regime != snap.regime

    conf = Decimal(str(round(confidence_from_snapshot(snap), 4)))
    probs = [
        {"regime": p.regime, "probability": float(p.probability)}
        for p in snap.regime_probabilities
    ]
    row = MarketStateRow(
        symbol=sym,
        timeframe=tf,
        regime=snap.regime,
        probabilities_json=json.dumps(probs, separators=(",", ":")),
        volatility_percentile=(
            Decimal(str(round(snap.volatility_percentile, 2)))
            if snap.volatility_percentile is not None
            else None
        ),
        trend_strength=(
            Decimal(str(round(snap.trend_strength, 4)))
            if snap.trend_strength is not None
            else None
        ),
        as_of=ensure_utc(snap.as_of),
        model_version=snap.model_version or REGIME_MODEL_VERSION,
        confidence=conf,
        stale=False,
        sources_json=json.dumps(["mt5.prices", snap.model_version or REGIME_MODEL_VERSION]),
    )
    # Always append latest classification for history; outbox only on change
    session.add(row)

    event_id: str | None = None
    if changed and enqueue_outbox:
        event_id = str(uuid4())
        occurred = ensure_utc(snap.as_of)
        envelope = RegimeChangedEvent(
            event_id=event_id,
            occurred_at=occurred,
            symbol=sym,
            provenance=Provenance(
                sources=["mt5.prices", snap.model_version or REGIME_MODEL_VERSION],
                generated_at=datetime.now(UTC),
                model_version=snap.model_version or REGIME_MODEL_VERSION,
                confidence=float(conf),
                stale=False,
            ),
            payload=RegimeChangedPayload(
                symbol=sym,
                timeframe=tf,  # type: ignore[arg-type]
                previous_regime=previous_regime,  # type: ignore[arg-type]
                new_regime=snap.regime,
                as_of=occurred,
            ),
        )
        session.add(
            OutboxMessage(
                event_id=event_id,
                event="regime.changed",
                payload_json=envelope.model_dump_json(),
            )
        )

    session.flush()
    return StatePersistResult(row=row, changed=changed, outbox_event_id=event_id)
