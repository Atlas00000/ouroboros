"""Contract schema smoke tests — Phase 0."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from contracts import (
    AssetProfile,
    Insight,
    MarketState,
    Provenance,
    RegimeChangedEvent,
    SentimentSnapshot,
)
from contracts.events_v1 import RegimeChangedPayload
from contracts.profile_v1 import AssetIdentity
from contracts.state_v1 import RegimeProbability


def _prov() -> Provenance:
    return Provenance(
        sources=["mt5"],
        generated_at=datetime.now(UTC),
        model_version="test_v1",
        confidence=0.85,
        stale=False,
    )


def test_asset_profile_roundtrip() -> None:
    profile = AssetProfile(
        profile_version=1,
        identity=AssetIdentity(
            symbol="EURUSD",
            display_name="Euro / US Dollar",
            asset_class="fx",
        ),
        as_of=datetime.now(UTC),
        provenance=_prov(),
    )
    data = profile.model_dump(mode="json")
    restored = AssetProfile.model_validate(data)
    assert restored.schema_id == "profile.v1"
    assert restored.identity.symbol == "EURUSD"


def test_market_state_requires_probability_sum() -> None:
    with pytest.raises(ValidationError):
        MarketState(
            symbol="EURUSD",
            timeframe="H1",
            regime="trending_up",
            regime_probabilities=[
                RegimeProbability(regime="trending_up", probability=0.5),
                RegimeProbability(regime="ranging", probability=0.2),
            ],
            as_of=datetime.now(UTC),
            provenance=_prov(),
        )


def test_market_state_ok() -> None:
    state = MarketState(
        symbol="EURUSD",
        timeframe="H1",
        regime="ranging",
        regime_probabilities=[
            RegimeProbability(regime="trending_up", probability=0.1),
            RegimeProbability(regime="trending_down", probability=0.1),
            RegimeProbability(regime="ranging", probability=0.7),
            RegimeProbability(regime="high_volatility", probability=0.1),
        ],
        as_of=datetime.now(UTC),
        provenance=_prov(),
    )
    assert state.schema_id == "state.v1"


def test_sentiment_bounds() -> None:
    snap = SentimentSnapshot(
        symbol="XAUUSD",
        score=-0.25,
        item_count=3,
        as_of=datetime.now(UTC),
        provenance=_prov(),
    )
    assert snap.schema_id == "sentiment.v1"
    with pytest.raises(ValidationError):
        SentimentSnapshot(
            symbol="XAUUSD",
            score=1.5,
            item_count=0,
            as_of=datetime.now(UTC),
            provenance=_prov(),
        )


def test_insight_is_narrative_only() -> None:
    insight = Insight(
        title="Quiet session",
        body="Range-bound price action into London open.",
        as_of=datetime.now(UTC),
        provenance=_prov(),
        symbol="EURUSD",
    )
    assert insight.type == "narrative"
    assert insight.schema_id == "insight.v1"


def test_regime_changed_event() -> None:
    event = RegimeChangedEvent(
        event_id="00000000-0000-0000-0000-000000000001",
        occurred_at=datetime.now(UTC),
        symbol="EURUSD",
        provenance=_prov(),
        payload=RegimeChangedPayload(
            symbol="EURUSD",
            timeframe="H1",
            previous_regime="ranging",
            new_regime="trending_up",
            as_of=datetime.now(UTC),
        ),
    )
    assert event.event == "regime.changed"
    assert event.schema_id == "events.v1"
