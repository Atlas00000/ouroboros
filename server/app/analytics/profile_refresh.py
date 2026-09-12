"""Event-triggered AssetProfile refresh (Phase 2 W5·D2).

Triggers:
  - confirmed regime flip on H4 or D1
  - high-impact calendar events mapped to a symbol

Debounce: ≤1 refresh / hour / symbol (via ``profiles.created_at``).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Literal

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analytics.bars import load_ohlcv, m1_depth_days
from app.analytics.profile_store import (
    REFRESH_COOLDOWN,
    can_refresh_symbol,
    next_profile_version,
    persist_asset_profile,
)
from app.analytics.profiles import build_asset_profile_from_session
from app.analytics.regimes import regime_feature_frame
from app.analytics.universe import passes_depth_gate
from app.calendar.timebase import ensure_utc
from app.models.asset import Asset
from app.models.news import NewsItem

RegimeTriggerTf = Literal["H4", "D1"]
REGIME_TRIGGER_TFS: tuple[RegimeTriggerTf, ...] = ("H4", "D1")

TriggerReason = Literal["regime.changed", "calendar.high_impact", "manual"]


@dataclass(frozen=True)
class RefreshTrigger:
    symbol: str
    reason: TriggerReason
    detail: str
    as_of: datetime


@dataclass
class RefreshOutcome:
    symbol: str
    reason: TriggerReason
    status: Literal["refreshed", "skipped_cooldown", "skipped_error", "skipped_unknown"]
    profile_version: int | None = None
    detail: str = ""


@dataclass
class RefreshReport:
    triggers: list[RefreshTrigger] = field(default_factory=list)
    outcomes: list[RefreshOutcome] = field(default_factory=list)

    @property
    def refreshed(self) -> int:
        return sum(1 for o in self.outcomes if o.status == "refreshed")


def confirmed_regime_flipped_on_last_bar(features: pd.DataFrame) -> tuple[str, str, datetime] | None:
    """
    If the last two confirmed labels differ, return (previous, new, as_of).
    """
    if features is None or len(features) < 2 or "confirmed_regime" not in features.columns:
        return None
    cur = features["confirmed_regime"].iloc[-1]
    prev = features["confirmed_regime"].iloc[-2]
    if cur is None or prev is None or pd.isna(cur) or pd.isna(prev):
        return None
    cur_s, prev_s = str(cur), str(prev)
    if cur_s == prev_s:
        return None
    as_of = ensure_utc(pd.to_datetime(features["ts"].iloc[-1], utc=True).to_pydatetime())
    return prev_s, cur_s, as_of


def detect_regime_change_triggers(
    session: Session,
    symbols: list[str],
    *,
    lookback_days: int = 120,
    timeframes: tuple[RegimeTriggerTf, ...] = REGIME_TRIGGER_TFS,
) -> list[RefreshTrigger]:
    """Scan H4/D1 for a confirmed-regime flip on the latest bar."""
    out: list[RefreshTrigger] = []
    seen: set[str] = set()
    for raw in symbols:
        sym = raw.upper()
        if sym in seen:
            continue
        span = m1_depth_days(session, sym)
        if not passes_depth_gate(sym, m1_span_days_value=span):
            continue
        for tf in timeframes:
            df = load_ohlcv(session, sym, tf, lookback_days=lookback_days)
            if df.empty or len(df) < 40:
                continue
            features = regime_feature_frame(df, tf)
            flip = confirmed_regime_flipped_on_last_bar(features)
            if flip is None:
                continue
            prev, new, as_of = flip
            out.append(
                RefreshTrigger(
                    symbol=sym,
                    reason="regime.changed",
                    detail=f"{tf}:{prev}->{new}",
                    as_of=as_of,
                )
            )
            seen.add(sym)
            break
    return out


def detect_high_impact_calendar_triggers(
    session: Session,
    *,
    now: datetime | None = None,
    lookback: timedelta = timedelta(hours=6),
    lookahead: timedelta = timedelta(hours=24),
) -> list[RefreshTrigger]:
    """Symbols with high-impact calendar rows in [now-lookback, now+lookahead]."""
    now_utc = ensure_utc(now or datetime.now(UTC))
    lo = now_utc - lookback
    hi = now_utc + lookahead
    rows = session.execute(
        select(NewsItem.symbol, NewsItem.scheduled_at, NewsItem.headline)
        .where(NewsItem.is_calendar.is_(True))
        .where(NewsItem.impact == "high")
        .where(NewsItem.symbol.is_not(None))
        .where(NewsItem.scheduled_at.is_not(None))
        .where(NewsItem.scheduled_at >= lo)
        .where(NewsItem.scheduled_at <= hi)
    ).all()

    out: list[RefreshTrigger] = []
    seen: set[str] = set()
    for symbol, scheduled_at, headline in rows:
        sym = str(symbol).upper()
        if sym in seen:
            continue
        seen.add(sym)
        as_of = ensure_utc(scheduled_at)
        title = (headline or "")[:80]
        out.append(
            RefreshTrigger(
                symbol=sym,
                reason="calendar.high_impact",
                detail=title,
                as_of=as_of,
            )
        )
    return out


def collect_refresh_triggers(
    session: Session,
    *,
    symbols: list[str] | None = None,
    now: datetime | None = None,
) -> list[RefreshTrigger]:
    """Union of regime + calendar triggers (deduped; regime wins detail if both)."""
    if symbols is None:
        symbols = [
            str(s)
            for s in session.scalars(select(Asset.symbol).where(Asset.is_active.is_(True))).all()
        ]
    regime = detect_regime_change_triggers(session, symbols)
    calendar = detect_high_impact_calendar_triggers(session, now=now)
    by_sym: dict[str, RefreshTrigger] = {t.symbol: t for t in calendar}
    for t in regime:
        by_sym[t.symbol] = t  # prefer regime.changed detail
    return sorted(by_sym.values(), key=lambda t: t.symbol)


def refresh_symbol_profile(
    session: Session,
    symbol: str,
    *,
    reason: TriggerReason = "manual",
    detail: str = "",
    now: datetime | None = None,
    peer_symbols: list[str] | None = None,
    force: bool = False,
    enqueue_outbox: bool = True,
) -> RefreshOutcome:
    """Build + persist one profile if cooldown allows."""
    sym = symbol.upper()
    now_utc = ensure_utc(now or datetime.now(UTC))
    if not force and not can_refresh_symbol(session, sym, now=now_utc, cooldown=REFRESH_COOLDOWN):
        return RefreshOutcome(
            symbol=sym,
            reason=reason,
            status="skipped_cooldown",
            detail=detail or "≤1 refresh/hour/symbol",
        )

    try:
        version = next_profile_version(session, sym)
        profile = build_asset_profile_from_session(
            session,
            sym,
            profile_version=version,
            peer_symbols=peer_symbols,
        )
        persist_asset_profile(session, profile, enqueue_outbox=enqueue_outbox, created_at=now_utc)
        return RefreshOutcome(
            symbol=sym,
            reason=reason,
            status="refreshed",
            profile_version=version,
            detail=detail,
        )
    except KeyError:
        return RefreshOutcome(
            symbol=sym,
            reason=reason,
            status="skipped_unknown",
            detail="asset not found",
        )
    except Exception as exc:  # noqa: BLE001 — surface per-symbol, continue batch
        return RefreshOutcome(
            symbol=sym,
            reason=reason,
            status="skipped_error",
            detail=str(exc)[:200],
        )


def run_event_triggered_refresh(
    session: Session,
    *,
    symbols: list[str] | None = None,
    now: datetime | None = None,
    peer_symbols: list[str] | None = None,
    force: bool = False,
    enqueue_outbox: bool = True,
    commit: bool = True,
) -> RefreshReport:
    """Detect triggers and refresh eligible symbols (W5·D2 orchestration)."""
    triggers = collect_refresh_triggers(session, symbols=symbols, now=now)
    report = RefreshReport(triggers=list(triggers))
    for trig in triggers:
        outcome = refresh_symbol_profile(
            session,
            trig.symbol,
            reason=trig.reason,
            detail=trig.detail,
            now=now,
            peer_symbols=peer_symbols,
            force=force,
            enqueue_outbox=enqueue_outbox,
        )
        report.outcomes.append(outcome)
    if commit:
        session.commit()
    return report
