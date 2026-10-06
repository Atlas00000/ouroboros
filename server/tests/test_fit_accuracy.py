"""Unit tests for fit stickiness scoring helpers."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta

from app.analytics.fit.mapper import map_regime_to_fit
from app.scoring.fit_accuracy import (
    SCORING_MODEL_VERSION,
    WeeklyFitAccuracyReport,
    _prediction_tag,
    build_weekly_fit_accuracy,
)


def test_map_regime_to_fit_meanrev_ranging() -> None:
    assert map_regime_to_fit("ranging", "meanrev") == "MATCH"
    assert map_regime_to_fit("trending_up", "meanrev") == "MISMATCH"
    assert map_regime_to_fit("high_volatility", "meanrev") == "FRAGILE"


def test_prediction_tag_parse() -> None:
    assert _prediction_tag(json.dumps({"tag": "MATCH", "family": "meanrev"})) == "MATCH"
    assert _prediction_tag(json.dumps({"skipped": True, "tag": "MATCH"})) is None


def test_weekly_fit_report_to_dict_delta() -> None:
    start = datetime(2026, 9, 29, tzinfo=UTC)
    end = start + timedelta(days=7)
    report = WeeklyFitAccuracyReport(
        week_start=start,
        week_end=end,
        n_scored=10,
        n_correct=6,
        n_persistence_correct=5,
    )
    d = report.to_dict()
    assert d["scoring_model"] == SCORING_MODEL_VERSION
    assert d["accuracy"] == 0.6
    assert d["persistence_accuracy"] == 0.5
    assert abs(d["delta_vs_persistence"] - 0.1) < 1e-9


def test_build_weekly_fit_accuracy_empty_session() -> None:
    class _Empty:
        def scalars(self, *_a, **_k):
            return self

        def all(self):
            return []

    class _Session:
        def scalars(self, *_a, **_k):
            return _Empty()

    report = build_weekly_fit_accuracy(
        _Session(),  # type: ignore[arg-type]
        week_start=datetime(2026, 9, 29, tzinfo=UTC),
        week_end=datetime(2026, 10, 6, tzinfo=UTC),
    )
    assert report.n_scored == 0
    assert report.accuracy is None
