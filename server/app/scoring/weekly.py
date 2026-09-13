"""Weekly scoring job — score due calls, persist report, email digest (W8·D1)."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.calendar.timebase import ensure_utc
from app.models.scoring_report import ScoringWeeklyReport
from app.notifications.base import AlertMessage, Notifier
from app.notifications.factory import build_notifier
from app.scoring.regime_accuracy import (
    ScoreBatchReport,
    WeeklyAccuracyReport,
    build_weekly_accuracy,
    format_weekly_email,
    score_due_regime_calls,
    week_window,
)

logger = logging.getLogger(__name__)


@dataclass
class WeeklyScoringResult:
    batch: ScoreBatchReport
    report: WeeklyAccuracyReport
    report_row_id: int | None
    email_ok: bool | None


def persist_weekly_report(
    session: Session,
    report: WeeklyAccuracyReport,
    *,
    email_sent_at: datetime | None = None,
) -> ScoringWeeklyReport:
    row = ScoringWeeklyReport(
        week_start=report.week_start,
        week_end=report.week_end,
        n_scored=report.n_scored,
        n_correct=report.n_correct,
        accuracy=(
            Decimal(str(round(report.accuracy, 4))) if report.accuracy is not None else None
        ),
        report_json=json.dumps(report.to_dict(), separators=(",", ":")),
        email_sent_at=email_sent_at,
    )
    session.add(row)
    session.flush()
    return row


def run_weekly_scoring(
    session: Session,
    *,
    notifier: Notifier | None = None,
    send_email: bool = True,
    commit: bool = True,
    now: datetime | None = None,
) -> WeeklyScoringResult:
    """
    1) Score due unscored regime calls
    2) Build previous-week accuracy tables
    3) Persist + optionally email via Resend/log notifier
    """
    now = ensure_utc(now or datetime.now(UTC))
    batch = score_due_regime_calls(session, now=now, commit=False)
    week_start, week_end = week_window(now)
    report = build_weekly_accuracy(
        session, week_start=week_start, week_end=week_end, now=now
    )

    email_ok: bool | None = None
    sent_at: datetime | None = None
    if send_email:
        channel = notifier or build_notifier()
        subject, body = format_weekly_email(report)
        result = channel.send(
            AlertMessage(
                subject=subject,
                body=body,
                severity="info",
                tags=("scoring", "weekly", "regime"),
            )
        )
        email_ok = bool(result.ok)
        if result.ok:
            sent_at = now
        logger.info(
            "weekly_scoring_email channel=%s ok=%s detail=%s",
            result.channel,
            result.ok,
            result.detail,
        )

    row = persist_weekly_report(session, report, email_sent_at=sent_at)
    if commit:
        session.commit()
    else:
        session.flush()

    logger.info(
        "weekly_scoring scored=%s correct_batch=%s week_acc=%s n=%s",
        batch.scored,
        batch.correct,
        report.accuracy,
        report.n_scored,
    )
    return WeeklyScoringResult(
        batch=batch,
        report=report,
        report_row_id=row.id,
        email_ok=email_ok,
    )
