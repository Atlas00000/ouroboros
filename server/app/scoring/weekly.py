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
from app.scoring.fit_accuracy import (
    WeeklyFitAccuracyReport,
    build_weekly_fit_accuracy,
    score_due_fit_calls,
)
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
    fit_batch: ScoreBatchReport
    report: WeeklyAccuracyReport
    fit_report: WeeklyFitAccuracyReport
    report_row_id: int | None
    email_ok: bool | None


def persist_weekly_report(
    session: Session,
    report: WeeklyAccuracyReport,
    *,
    fit_report: WeeklyFitAccuracyReport | None = None,
    email_sent_at: datetime | None = None,
) -> ScoringWeeklyReport:
    payload = report.to_dict()
    if fit_report is not None:
        payload["fit"] = fit_report.to_dict()
    row = ScoringWeeklyReport(
        week_start=report.week_start,
        week_end=report.week_end,
        n_scored=report.n_scored,
        n_correct=report.n_correct,
        accuracy=(
            Decimal(str(round(report.accuracy, 4))) if report.accuracy is not None else None
        ),
        report_json=json.dumps(payload, separators=(",", ":")),
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
    1) Score due unscored regime + fit calls
    2) Build previous-week accuracy tables (regime + fit vs persistence)
    3) Persist + optionally email via Resend/log notifier
    """
    now = ensure_utc(now or datetime.now(UTC))
    batch = score_due_regime_calls(session, now=now, commit=False)
    fit_batch = score_due_fit_calls(session, now=now, commit=False)
    week_start, week_end = week_window(now)
    report = build_weekly_accuracy(
        session, week_start=week_start, week_end=week_end, now=now
    )
    fit_report = build_weekly_fit_accuracy(
        session, week_start=week_start, week_end=week_end, now=now
    )

    email_ok: bool | None = None
    sent_at: datetime | None = None
    if send_email:
        channel = notifier or build_notifier()
        subject, body = format_weekly_email(report)
        # Append fit honesty block
        fit_acc = (
            f"{fit_report.accuracy:.1%}" if fit_report.accuracy is not None else "n/a"
        )
        persist_acc = (
            f"{fit_report.persistence_accuracy:.1%}"
            if fit_report.persistence_accuracy is not None
            else "n/a"
        )
        body = (
            body
            + "\n\nFit stickiness (scoring.fit.v1):\n"
            + f"  Overall: {fit_report.n_correct}/{fit_report.n_scored} = {fit_acc}\n"
            + f"  Persistence baseline: {persist_acc}\n"
            + f"  Delta vs persistence: {fit_report.delta_vs_persistence}\n"
        )
        result = channel.send(
            AlertMessage(
                subject=subject,
                body=body,
                severity="info",
                tags=("scoring", "weekly", "regime", "fit"),
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

    row = persist_weekly_report(
        session, report, fit_report=fit_report, email_sent_at=sent_at
    )
    if commit:
        session.commit()
    else:
        session.flush()

    logger.info(
        "weekly_scoring scored=%s correct_batch=%s fit_scored=%s week_acc=%s n=%s",
        batch.scored,
        batch.correct,
        fit_batch.scored,
        report.accuracy,
        report.n_scored,
    )
    return WeeklyScoringResult(
        batch=batch,
        fit_batch=fit_batch,
        report=report,
        fit_report=fit_report,
        report_row_id=row.id,
        email_ok=email_ok,
    )
