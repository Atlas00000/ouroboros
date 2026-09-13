"""Regime call scoring — fill realized_json / score on forecast_log (W8·D1)."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analytics.bars import load_ohlcv, m1_depth_days
from app.analytics.forecast_log import HORIZON_MINUTES
from app.analytics.regimes import classify_regime
from app.calendar.timebase import ensure_utc
from app.models.forecast_log import ForecastLog

logger = logging.getLogger(__name__)

SCORING_MODEL_VERSION = "scoring.regime.v1"
MAX_SCORE_BATCH = 200


@dataclass
class ScoreBatchReport:
    attempted: int = 0
    scored: int = 0
    skipped: int = 0
    correct: int = 0
    errors: list[str] = field(default_factory=list)


def _prediction_regime(prediction_json: str) -> str | None:
    try:
        data = json.loads(prediction_json)
    except json.JSONDecodeError:
        return None
    if data.get("skipped"):
        return None
    regime = data.get("regime")
    return str(regime) if regime else None


def score_due_regime_calls(
    session: Session,
    *,
    now: datetime | None = None,
    limit: int = MAX_SCORE_BATCH,
    commit: bool = True,
) -> ScoreBatchReport:
    """
    Score unscored regime calls whose horizon has elapsed.

    Realized outcome = regime re-classified on bars ending at made_at + horizon.
    Score is 1.0 (hit) or 0.0 (miss). Skipped predictions are left unscored.
    """
    now = ensure_utc(now or datetime.now(UTC))
    report = ScoreBatchReport()

    rows = list(
        session.scalars(
            select(ForecastLog)
            .where(
                ForecastLog.call_type == "regime",
                ForecastLog.scored_at.is_(None),
            )
            .order_by(ForecastLog.made_at.asc())
            .limit(limit * 3)  # over-fetch; filter horizon below
        ).all()
    )

    for row in rows:
        if report.attempted >= limit:
            break
        horizon = row.horizon_minutes or HORIZON_MINUTES.get(row.timeframe, 60)
        eval_at = ensure_utc(row.made_at) + timedelta(minutes=int(horizon))
        if eval_at > now:
            continue

        predicted = _prediction_regime(row.prediction_json)
        if predicted is None:
            report.skipped += 1
            # Mark scored with null outcome so we don't retry forever
            row.realized_json = json.dumps({"skipped_prediction": True})
            row.scored_at = now
            row.score = None
            continue

        report.attempted += 1
        try:
            span = m1_depth_days(session, row.symbol)
            df = load_ohlcv(
                session,
                row.symbol,
                row.timeframe,  # type: ignore[arg-type]
                lookback_days=120,
                end_utc=eval_at,
            )
            if df.empty or len(df) < 30:
                report.skipped += 1
                row.realized_json = json.dumps({"error": "insufficient_bars", "eval_at": eval_at.isoformat()})
                row.scored_at = now
                row.score = None
                continue

            snap = classify_regime(
                df,
                symbol=row.symbol,
                timeframe=row.timeframe,  # type: ignore[arg-type]
                m1_span_days_value=span,
            )
            if snap.skipped:
                report.skipped += 1
                row.realized_json = json.dumps(
                    {
                        "skipped": True,
                        "skip_reason": snap.skip_reason,
                        "eval_at": eval_at.isoformat(),
                    }
                )
                row.scored_at = now
                row.score = None
                continue

            hit = snap.regime == predicted
            score = 1.0 if hit else 0.0
            realized: dict[str, Any] = {
                "regime": snap.regime,
                "raw_regime": snap.raw_regime,
                "predicted": predicted,
                "hit": hit,
                "eval_at": ensure_utc(snap.as_of).isoformat(),
                "horizon_minutes": horizon,
                "scoring_model": SCORING_MODEL_VERSION,
            }
            row.realized_json = json.dumps(realized, separators=(",", ":"))
            row.scored_at = now
            row.score = Decimal(str(score))
            report.scored += 1
            if hit:
                report.correct += 1
        except Exception as exc:  # noqa: BLE001
            msg = f"{row.symbol}/{row.timeframe} id={row.id}: {exc}"
            report.errors.append(msg[:200])
            logger.warning("score_regime_failed %s", msg)

    if commit:
        session.commit()
    else:
        session.flush()
    return report


@dataclass
class AccuracyBucket:
    symbol: str
    timeframe: str
    model_version: str
    n: int = 0
    correct: int = 0

    @property
    def accuracy(self) -> float | None:
        if self.n == 0:
            return None
        return self.correct / self.n


@dataclass
class WeeklyAccuracyReport:
    week_start: datetime
    week_end: datetime
    buckets: list[AccuracyBucket] = field(default_factory=list)
    n_scored: int = 0
    n_correct: int = 0

    @property
    def accuracy(self) -> float | None:
        if self.n_scored == 0:
            return None
        return self.n_correct / self.n_scored

    def to_dict(self) -> dict[str, Any]:
        return {
            "week_start": self.week_start.isoformat(),
            "week_end": self.week_end.isoformat(),
            "n_scored": self.n_scored,
            "n_correct": self.n_correct,
            "accuracy": self.accuracy,
            "by_symbol_tf": [
                {
                    "symbol": b.symbol,
                    "timeframe": b.timeframe,
                    "model_version": b.model_version,
                    "n": b.n,
                    "correct": b.correct,
                    "accuracy": b.accuracy,
                }
                for b in self.buckets
            ],
            "scoring_model": SCORING_MODEL_VERSION,
        }


def week_window(now: datetime | None = None) -> tuple[datetime, datetime]:
    """Previous complete UTC week Mon 00:00 → next Mon 00:00."""
    now = ensure_utc(now or datetime.now(UTC))
    # weekday: Mon=0 … Sun=6
    start_of_this_week = (now - timedelta(days=now.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    week_end = start_of_this_week
    week_start = week_end - timedelta(days=7)
    return week_start, week_end


def build_weekly_accuracy(
    session: Session,
    *,
    week_start: datetime | None = None,
    week_end: datetime | None = None,
    now: datetime | None = None,
) -> WeeklyAccuracyReport:
    if week_start is None or week_end is None:
        week_start, week_end = week_window(now)
    week_start = ensure_utc(week_start)
    week_end = ensure_utc(week_end)

    rows = list(
        session.scalars(
            select(ForecastLog).where(
                ForecastLog.call_type == "regime",
                ForecastLog.scored_at.is_not(None),
                ForecastLog.score.is_not(None),
                ForecastLog.made_at >= week_start,
                ForecastLog.made_at < week_end,
            )
        ).all()
    )

    grouped: dict[tuple[str, str, str], AccuracyBucket] = {}
    n_scored = 0
    n_correct = 0
    for row in rows:
        key = (row.symbol, row.timeframe, row.model_version)
        if key not in grouped:
            grouped[key] = AccuracyBucket(
                symbol=row.symbol,
                timeframe=row.timeframe,
                model_version=row.model_version,
            )
        bucket = grouped[key]
        bucket.n += 1
        n_scored += 1
        if float(row.score or 0) >= 0.5:
            bucket.correct += 1
            n_correct += 1

    buckets = sorted(grouped.values(), key=lambda b: (b.symbol, b.timeframe))
    return WeeklyAccuracyReport(
        week_start=week_start,
        week_end=week_end,
        buckets=buckets,
        n_scored=n_scored,
        n_correct=n_correct,
    )


def format_weekly_email(report: WeeklyAccuracyReport) -> tuple[str, str]:
    acc = f"{report.accuracy:.1%}" if report.accuracy is not None else "n/a"
    subject = (
        f"Ouroboros weekly regime accuracy — {acc} "
        f"({report.n_correct}/{report.n_scored})"
    )
    lines = [
        f"Week: {report.week_start.date()} → {report.week_end.date()} (UTC)",
        f"Overall: {report.n_correct}/{report.n_scored} = {acc}",
        f"Model: {SCORING_MODEL_VERSION}",
        "",
        "By symbol / timeframe:",
    ]
    if not report.buckets:
        lines.append("  (no scored regime calls in window)")
    for b in report.buckets:
        b_acc = f"{b.accuracy:.1%}" if b.accuracy is not None else "n/a"
        lines.append(
            f"  {b.symbol} {b.timeframe} ({b.model_version}): "
            f"{b.correct}/{b.n} = {b_acc}"
        )
    lines.append("")
    lines.append("Research only — not investment advice; no trade execution.")
    return subject, "\n".join(lines)
