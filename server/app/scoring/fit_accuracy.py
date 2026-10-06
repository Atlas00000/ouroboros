"""Fit-tag stickiness scoring — score forecast_log fit.* rows (scoring.fit.v1)."""

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
from app.analytics.fit.mapper import family_from_call_type, map_regime_to_fit
from app.analytics.forecast_log import HORIZON_MINUTES
from app.analytics.regimes import classify_regime
from app.calendar.timebase import ensure_utc
from app.models.forecast_log import ForecastLog
from app.scoring.regime_accuracy import ScoreBatchReport, week_window

logger = logging.getLogger(__name__)

SCORING_MODEL_VERSION = "scoring.fit.v1"
FIT_CALL_TYPES = ("fit.meanrev", "fit.trendfollow")
MAX_SCORE_BATCH = 200


def _prediction_tag(prediction_json: str) -> str | None:
    try:
        data = json.loads(prediction_json)
    except json.JSONDecodeError:
        return None
    if data.get("skipped"):
        return None
    tag = data.get("tag")
    return str(tag) if tag else None


def score_due_fit_calls(
    session: Session,
    *,
    now: datetime | None = None,
    limit: int = MAX_SCORE_BATCH,
    commit: bool = True,
) -> ScoreBatchReport:
    """
    Score unscored fit.* calls whose horizon has elapsed.

    Realized = re-classify regime at made_at + horizon, then fit.map_v0 → tag.
    Score is 1.0 (hit) or 0.0 (miss).
    """
    now = ensure_utc(now or datetime.now(UTC))
    report = ScoreBatchReport()

    rows = list(
        session.scalars(
            select(ForecastLog)
            .where(
                ForecastLog.call_type.in_(FIT_CALL_TYPES),
                ForecastLog.scored_at.is_(None),
            )
            .order_by(ForecastLog.made_at.asc())
            .limit(limit * 3)
        ).all()
    )

    for row in rows:
        if report.attempted >= limit:
            break
        horizon = row.horizon_minutes or HORIZON_MINUTES.get(row.timeframe, 60)
        eval_at = ensure_utc(row.made_at) + timedelta(minutes=int(horizon))
        if eval_at > now:
            continue

        predicted = _prediction_tag(row.prediction_json)
        if predicted is None:
            report.skipped += 1
            row.realized_json = json.dumps({"skipped_prediction": True})
            row.scored_at = now
            row.score = None
            continue

        try:
            family = family_from_call_type(row.call_type)
        except ValueError:
            report.skipped += 1
            row.realized_json = json.dumps({"error": "bad_call_type", "call_type": row.call_type})
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
                row.realized_json = json.dumps(
                    {"error": "insufficient_bars", "eval_at": eval_at.isoformat()}
                )
                row.scored_at = now
                row.score = None
                continue

            snap = classify_regime(
                df,
                symbol=row.symbol,
                timeframe=row.timeframe,  # type: ignore[arg-type]
                m1_span_days_value=span,
            )
            if snap.skipped or not snap.regime:
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

            realized_tag = map_regime_to_fit(snap.regime, family)
            hit = realized_tag == predicted
            score = 1.0 if hit else 0.0
            realized: dict[str, Any] = {
                "tag": realized_tag,
                "regime": snap.regime,
                "predicted": predicted,
                "family": family,
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
            msg = f"{row.symbol}/{row.timeframe}/{row.call_type} id={row.id}: {exc}"
            report.errors.append(msg[:200])
            logger.warning("score_fit_failed %s", msg)

    if commit:
        session.commit()
    else:
        session.flush()
    return report


@dataclass
class FitFamilyBucket:
    family: str
    timeframe: str
    n: int = 0
    correct: int = 0
    persistence_correct: int = 0

    @property
    def accuracy(self) -> float | None:
        if self.n == 0:
            return None
        return self.correct / self.n

    @property
    def persistence_accuracy(self) -> float | None:
        if self.n == 0:
            return None
        return self.persistence_correct / self.n


@dataclass
class WeeklyFitAccuracyReport:
    week_start: datetime
    week_end: datetime
    buckets: list[FitFamilyBucket] = field(default_factory=list)
    n_scored: int = 0
    n_correct: int = 0
    n_persistence_correct: int = 0

    @property
    def accuracy(self) -> float | None:
        if self.n_scored == 0:
            return None
        return self.n_correct / self.n_scored

    @property
    def persistence_accuracy(self) -> float | None:
        if self.n_scored == 0:
            return None
        return self.n_persistence_correct / self.n_scored

    @property
    def delta_vs_persistence(self) -> float | None:
        if self.accuracy is None or self.persistence_accuracy is None:
            return None
        return self.accuracy - self.persistence_accuracy

    def to_dict(self) -> dict[str, Any]:
        return {
            "week_start": self.week_start.isoformat(),
            "week_end": self.week_end.isoformat(),
            "n_scored": self.n_scored,
            "n_correct": self.n_correct,
            "accuracy": self.accuracy,
            "persistence_correct": self.n_persistence_correct,
            "persistence_accuracy": self.persistence_accuracy,
            "delta_vs_persistence": self.delta_vs_persistence,
            "by_family": [
                {
                    "family": b.family,
                    "timeframe": b.timeframe,
                    "n": b.n,
                    "correct": b.correct,
                    "accuracy": b.accuracy,
                    "persistence_correct": b.persistence_correct,
                    "persistence_accuracy": b.persistence_accuracy,
                }
                for b in self.buckets
            ],
            "scoring_model": SCORING_MODEL_VERSION,
        }


def build_weekly_fit_accuracy(
    session: Session,
    *,
    week_start: datetime | None = None,
    week_end: datetime | None = None,
    now: datetime | None = None,
) -> WeeklyFitAccuracyReport:
    """
    Fit stickiness vs persistence baseline for the week.

    Persistence = previous scored tag for same (symbol, timeframe, call_type);
    if none, baseline predicts MATCH.
    """
    if week_start is None or week_end is None:
        week_start, week_end = week_window(now)
    week_start = ensure_utc(week_start)
    week_end = ensure_utc(week_end)

    rows = list(
        session.scalars(
            select(ForecastLog)
            .where(
                ForecastLog.call_type.in_(FIT_CALL_TYPES),
                ForecastLog.scored_at.is_not(None),
                ForecastLog.score.is_not(None),
                ForecastLog.made_at >= week_start,
                ForecastLog.made_at < week_end,
            )
            .order_by(ForecastLog.made_at.asc())
        ).all()
    )

    # Prior tag cache for persistence: load last scored before week for each key.
    prior: dict[tuple[str, str, str], str] = {}
    priors = list(
        session.scalars(
            select(ForecastLog)
            .where(
                ForecastLog.call_type.in_(FIT_CALL_TYPES),
                ForecastLog.scored_at.is_not(None),
                ForecastLog.score.is_not(None),
                ForecastLog.made_at < week_start,
            )
            .order_by(ForecastLog.made_at.asc())
        ).all()
    )
    for row in priors:
        tag = _prediction_tag(row.prediction_json)
        if tag:
            prior[(row.symbol, row.timeframe, row.call_type)] = tag

    grouped: dict[tuple[str, str], FitFamilyBucket] = {}
    n_scored = 0
    n_correct = 0
    n_persist = 0

    for row in rows:
        try:
            family = family_from_call_type(row.call_type)
        except ValueError:
            continue
        key = (family, row.timeframe)
        if key not in grouped:
            grouped[key] = FitFamilyBucket(family=family, timeframe=row.timeframe)
        bucket = grouped[key]
        bucket.n += 1
        n_scored += 1

        pred = _prediction_tag(row.prediction_json)
        realized_tag: str | None = None
        try:
            realized = json.loads(row.realized_json or "{}")
            realized_tag = str(realized["tag"]) if realized.get("tag") else None
        except json.JSONDecodeError:
            realized_tag = None

        hit = float(row.score or 0) >= 0.5
        if hit:
            bucket.correct += 1
            n_correct += 1

        pkey = (row.symbol, row.timeframe, row.call_type)
        persist_pred = prior.get(pkey, "MATCH")
        if realized_tag is not None and persist_pred == realized_tag:
            bucket.persistence_correct += 1
            n_persist += 1

        if pred:
            prior[pkey] = pred

    buckets = sorted(grouped.values(), key=lambda b: (b.family, b.timeframe))
    return WeeklyFitAccuracyReport(
        week_start=week_start,
        week_end=week_end,
        buckets=buckets,
        n_scored=n_scored,
        n_correct=n_correct,
        n_persistence_correct=n_persist,
    )
