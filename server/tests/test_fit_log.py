"""Fit forecast_log writer helpers (R3)."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy import delete, text

from app.analytics.fit.gate import fit_from_regime_snapshot
from app.analytics.fit.log import fit_prediction_payload, log_fit_call
from app.analytics.fit.mapper import MODEL_VERSION, call_type_for_family
from app.analytics.regimes import RegimeProbability, RegimeSnapshot
from app.db.session import get_session_factory
from app.models.forecast_log import ForecastLog


def _regime_snap() -> RegimeSnapshot:
    return RegimeSnapshot(
        symbol="EURUSD",
        timeframe="H1",
        regime="ranging",
        raw_regime="ranging",
        regime_probabilities=(
            RegimeProbability("trending_up", 0.1),
            RegimeProbability("trending_down", 0.1),
            RegimeProbability("ranging", 0.7),
            RegimeProbability("high_volatility", 0.1),
        ),
        volatility_percentile=40.0,
        trend_strength=0.1,
        as_of=datetime(2026, 10, 1, 15, 0, tzinfo=UTC),
        model_version="regimes.rule_v1",
    )


def _db_session():
    try:
        session = get_session_factory()()
        session.execute(text("SELECT 1"))
        return session
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"database unavailable: {exc}")


def test_fit_prediction_payload() -> None:
    fit = fit_from_regime_snapshot(_regime_snap(), "meanrev")
    payload = fit_prediction_payload(fit)
    assert payload["tag"] == "MATCH"
    assert payload["family"] == "meanrev"
    assert payload["allow_on"] is True
    assert payload["regime"] == "ranging"


def test_log_fit_call_idempotent() -> None:
    fit = fit_from_regime_snapshot(_regime_snap(), "meanrev")
    session = _db_session()
    try:
        session.execute(
            delete(ForecastLog).where(
                ForecastLog.symbol == "EURUSD",
                ForecastLog.timeframe == "H1",
                ForecastLog.call_type == call_type_for_family("meanrev"),
                ForecastLog.made_at == fit.as_of,
                ForecastLog.model_version == MODEL_VERSION,
            )
        )
        session.commit()

        first = log_fit_call(session, fit, skip_duplicates=True)
        session.commit()
        assert first.inserted is True
        assert first.call_type == "fit.meanrev"

        second = log_fit_call(session, fit, skip_duplicates=True)
        session.commit()
        assert second.inserted is False
        assert second.row is not None
        assert first.row is not None
        assert second.row.id == first.row.id
    finally:
        session.execute(
            delete(ForecastLog).where(
                ForecastLog.symbol == "EURUSD",
                ForecastLog.timeframe == "H1",
                ForecastLog.call_type == "fit.meanrev",
                ForecastLog.made_at == fit.as_of,
                ForecastLog.model_version == MODEL_VERSION,
            )
        )
        session.commit()
        session.close()
