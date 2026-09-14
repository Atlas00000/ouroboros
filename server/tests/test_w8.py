"""W8 unit tests — scoring, staleness helpers, prometheus text, weekly email."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.api.staleness import ENDPOINT_FEED_MAP, any_feed_stale, endpoint_stale
from app.notifications.base import AlertMessage, SendResult
from app.observability.prom_metrics import observe_request, render_prometheus_text, reset_http_metrics
from app.scoring.regime_accuracy import (
    WeeklyAccuracyReport,
    AccuracyBucket,
    format_weekly_email,
    week_window,
    _prediction_regime,
)
from app.scoring.weekly import persist_weekly_report, run_weekly_scoring
from app.models.forecast_log import ForecastLog
from app.models.scoring_report import ScoringWeeklyReport


def test_prediction_regime_skips_skipped() -> None:
    assert _prediction_regime(json.dumps({"skipped": True, "regime": "ranging"})) is None
    assert _prediction_regime(json.dumps({"regime": "trending_up"})) == "trending_up"


def test_week_window_is_previous_utc_week() -> None:
    # Wednesday 2026-09-16 → previous week Mon 2026-09-07 → Mon 2026-09-14
    now = datetime(2026, 9, 16, 12, 0, tzinfo=UTC)
    start, end = week_window(now)
    assert start == datetime(2026, 9, 7, 0, 0, tzinfo=UTC)
    assert end == datetime(2026, 9, 14, 0, 0, tzinfo=UTC)


def test_format_weekly_email() -> None:
    report = WeeklyAccuracyReport(
        week_start=datetime(2026, 9, 7, tzinfo=UTC),
        week_end=datetime(2026, 9, 14, tzinfo=UTC),
        buckets=[
            AccuracyBucket(
                symbol="EURUSD",
                timeframe="H1",
                model_version="regimes.rule_v1",
                n=10,
                correct=6,
            )
        ],
        n_scored=10,
        n_correct=6,
    )
    subject, body = format_weekly_email(report)
    assert "60.0%" in subject or "60%" in subject
    assert "EURUSD" in body
    assert "not investment advice" in body.lower() or "Research only" in body


def test_prometheus_render_contains_http_counters() -> None:
    reset_http_metrics()
    observe_request(
        method="GET",
        path="/v1/assets",
        status=200,
        duration_sec=0.02,
        auth_method="api_key",
    )
    text = render_prometheus_text(
        extra_gauges={
            "ouroboros_llm_spend_usd_day": ("spend", {(): 1.25}),
        }
    )
    assert "ouroboros_http_requests_total" in text
    assert "ouroboros_auth_method_total" in text
    assert 'method="api_key"' in text
    assert "ouroboros_llm_spend_usd_day" in text
    reset_http_metrics()


def test_endpoint_feed_map_covers_data_routes() -> None:
    for ep in ("assets", "metrics", "bars", "state", "profiles", "news", "sentiment", "insights"):
        assert ep in ENDPOINT_FEED_MAP


def test_any_feed_stale_from_registry() -> None:
    class FakeSession:
        def scalars(self, _stmt):
            return SimpleNamespace(
                all=lambda: [
                    SimpleNamespace(source_id="mt5.prices", status="stale"),
                    SimpleNamespace(source_id="finnhub.news", status="ok"),
                ]
            )

    assert any_feed_stale(FakeSession(), ("mt5.prices",)) is True
    assert any_feed_stale(FakeSession(), ("finnhub.news",)) is False
    assert endpoint_stale(FakeSession(), "metrics") is True


def test_persist_weekly_report_row_type() -> None:
    report = WeeklyAccuracyReport(
        week_start=datetime(2026, 9, 7, tzinfo=UTC),
        week_end=datetime(2026, 9, 14, tzinfo=UTC),
        n_scored=0,
        n_correct=0,
    )
    added: list[object] = []

    class FakeSession:
        def add(self, obj: object) -> None:
            added.append(obj)

        def flush(self) -> None:
            # Assign id for callers
            if added:
                added[0].id = 42  # type: ignore[attr-defined]

    row = persist_weekly_report(FakeSession(), report)
    assert isinstance(row, ScoringWeeklyReport)
    assert row.n_scored == 0


class _LogNotifier:
    name = "log"

    def __init__(self) -> None:
        self.messages: list[AlertMessage] = []

    def send(self, message: AlertMessage) -> SendResult:
        self.messages.append(message)
        return SendResult(channel=self.name, ok=True, detail="logged")


def test_run_weekly_scoring_sends_email(monkeypatch: pytest.MonkeyPatch) -> None:
    notifier = _LogNotifier()

    def fake_score(session, *, now=None, commit=True, limit=200):
        from app.scoring.regime_accuracy import ScoreBatchReport

        return ScoreBatchReport(scored=0, correct=0)

    def fake_build(session, *, week_start=None, week_end=None, now=None):
        return WeeklyAccuracyReport(
            week_start=datetime(2026, 9, 7, tzinfo=UTC),
            week_end=datetime(2026, 9, 14, tzinfo=UTC),
            n_scored=4,
            n_correct=2,
        )

    monkeypatch.setattr("app.scoring.weekly.score_due_regime_calls", fake_score)
    monkeypatch.setattr("app.scoring.weekly.build_weekly_accuracy", fake_build)

    class FakeSession:
        def add(self, obj: object) -> None:
            obj.id = 7  # type: ignore[attr-defined]

        def flush(self) -> None:
            return None

        def commit(self) -> None:
            return None

    result = run_weekly_scoring(
        FakeSession(),
        notifier=notifier,
        send_email=True,
        commit=True,
        now=datetime(2026, 9, 16, tzinfo=UTC),
    )
    assert result.email_ok is True
    assert len(notifier.messages) == 1
    assert "accuracy" in notifier.messages[0].subject.lower() or "%" in notifier.messages[0].subject
    assert result.report_row_id == 7


def test_score_due_marks_skipped_prediction() -> None:
    """Unit: skipped prediction gets scored_at without requiring bars."""
    from app.scoring.regime_accuracy import score_due_regime_calls

    now = datetime(2026, 9, 13, 12, 0, tzinfo=UTC)
    row = ForecastLog(
        id=1,
        symbol="EURUSD",
        timeframe="H1",
        call_type="regime",
        prediction_json=json.dumps({"skipped": True, "regime": "ranging"}),
        model_version="regimes.rule_v1",
        confidence=Decimal("0"),
        made_at=now - timedelta(hours=2),
        horizon_minutes=60,
        realized_json=None,
        scored_at=None,
        score=None,
        created_at=now,
    )

    class FakeScalars:
        def all(self):
            return [row]

    class FakeSession:
        def scalars(self, _stmt):
            return FakeScalars()

        def commit(self) -> None:
            return None

        def flush(self) -> None:
            return None

    report = score_due_regime_calls(FakeSession(), now=now, commit=True)
    assert report.skipped == 1
    assert row.scored_at is not None
    assert row.score is None
