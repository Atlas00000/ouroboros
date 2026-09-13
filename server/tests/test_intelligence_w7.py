"""W7 guardrails — LLM budget, sentiment cache, narratives never touch numerics."""

from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace

import pytest

os.environ.setdefault("LLM_PROVIDERS", "mock")
os.environ.setdefault("LLM_PROVIDER", "mock")
os.environ.setdefault("LLM_DAILY_BUDGET_USD", "10")

from app.config import get_settings
from app.intelligence.llm_client import (
    BudgetExceededError,
    LLMClient,
    get_daily_spend_usd,
    heuristic_sentiment_score,
    record_spend,
    reset_spend_fallback,
)
from app.intelligence.narratives import (
    NARRATIVE_MODEL_VERSION,
    build_narrative_insight,
    persist_insight,
)
from app.intelligence.sentiment import (
    SENTIMENT_MODEL_VERSION,
    aggregate_symbol_sentiment,
    decay_weight,
    persist_sentiment,
    score_unseen_articles,
)
from app.models.article_score import ArticleScoreRow
from app.models.insight import InsightRow
from app.models.news import NewsItem
from app.models.outbox import OutboxMessage
from app.models.sentiment import SentimentRow
from contracts.common_v1 import Provenance
from contracts.state_v1 import MarketState, RegimeProbability


@pytest.fixture(autouse=True)
def _mock_llm_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_PROVIDERS", "mock")
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    monkeypatch.setenv("LLM_DAILY_BUDGET_USD", "10")
    get_settings.cache_clear()
    reset_spend_fallback()
    yield
    reset_spend_fallback()
    get_settings.cache_clear()


def test_heuristic_score_bounded() -> None:
    s = heuristic_sentiment_score("Markets crash amid recession fear")
    assert -1.0 <= s <= 1.0
    assert s < 0


def test_decay_weight_halves_at_half_life() -> None:
    assert decay_weight(0.0) == pytest.approx(1.0)
    assert decay_weight(12.0) == pytest.approx(0.5)


def test_budget_cap_raises() -> None:
    reset_spend_fallback()
    # Force in-process path by recording until over budget check
    record_spend(10.0)
    assert get_daily_spend_usd() >= 10.0
    client = LLMClient()
    with pytest.raises(BudgetExceededError):
        client.complete("hello")


def test_mock_provider_chain() -> None:
    client = LLMClient()
    assert client.provider_chain() == ["mock"]
    score, resp = client.score_headline("USD rally surge strong", symbol="EURUSD")
    assert -1.0 <= score <= 1.0
    assert resp.provider == "mock"


def test_score_unseen_articles_caches(monkeypatch: pytest.MonkeyPatch) -> None:
    now = datetime.now(UTC)
    items = [
        NewsItem(
            external_id="w7-art-1",
            symbol="EURUSD",
            headline="Euro rally surge optimism",
            source="test",
            published_at=now,
        )
    ]
    added: list[object] = []

    class FakeSession:
        def scalars(self, _stmt):
            return SimpleNamespace(all=lambda: [])

        def add(self, obj: object) -> None:
            added.append(obj)

        def flush(self) -> None:
            return None

    scored, cached = score_unseen_articles(FakeSession(), items, LLMClient(), max_new=10)
    assert scored == 1
    assert cached == 0
    assert len(added) == 1
    assert isinstance(added[0], ArticleScoreRow)

    # Second pass: treat as cached
    class FakeSession2:
        def scalars(self, _stmt):
            return SimpleNamespace(
                all=lambda: [
                    SimpleNamespace(external_id="w7-art-1", score=Decimal("0.5"))
                ]
            )

        def add(self, obj: object) -> None:
            raise AssertionError("must not re-score cached article")

        def flush(self) -> None:
            return None

    scored2, cached2 = score_unseen_articles(FakeSession2(), items, LLMClient(), max_new=10)
    assert scored2 == 0
    assert cached2 == 1


def test_narrative_is_labeled_and_has_disclaimer() -> None:
    state = MarketState(
        symbol="EURUSD",
        timeframe="H1",
        regime="ranging",
        regime_probabilities=[
            RegimeProbability(regime="ranging", probability=0.7),
            RegimeProbability(regime="trending_up", probability=0.1),
            RegimeProbability(regime="trending_down", probability=0.1),
            RegimeProbability(regime="high_volatility", probability=0.1),
        ],
        volatility_percentile=55.0,
        trend_strength=0.2,
        as_of=datetime.now(UTC),
        provenance=Provenance(
            sources=["test"],
            generated_at=datetime.now(UTC),
            model_version="regimes.rule_v1",
            confidence=0.7,
        ),
    )
    insight = build_narrative_insight("EURUSD", state=state, sentiment=None, client=LLMClient())
    assert insight.type == "narrative"
    assert insight.schema_id == "insight.v1"
    assert insight.disclaimer.text
    assert "not investment advice" in insight.disclaimer.text.lower() or "research" in insight.disclaimer.text.lower()
    assert insight.provenance.model_version == NARRATIVE_MODEL_VERSION
    assert SENTIMENT_MODEL_VERSION  # model constant imported / present


def test_persist_insight_only_adds_insight_row() -> None:
    insight = build_narrative_insight("EURUSD", state=None, sentiment=None, client=LLMClient())
    added: list[object] = []

    class FakeSession:
        def add(self, obj: object) -> None:
            added.append(obj)

        def flush(self) -> None:
            return None

    persist_insight(FakeSession(), insight)
    assert len(added) == 1
    assert isinstance(added[0], InsightRow)
    # Guardrail: never MarketStateRow / SentimentRow / price models
    assert not any(type(o).__name__ in {"MarketStateRow", "SentimentRow", "PriceBar"} for o in added)


def test_persist_sentiment_emits_spike_outbox() -> None:
    now = datetime.now(UTC)
    from contracts.sentiment_v1 import SentimentSnapshot

    prev = SentimentRow(
        id=1,
        symbol="EURUSD",
        score=Decimal("0.10"),
        item_count=2,
        window_hours=24,
        top_drivers_json="[]",
        as_of=now - timedelta(hours=1),
        model_version=SENTIMENT_MODEL_VERSION,
        confidence=Decimal("0.5"),
        stale=False,
        sources_json='["test"]',
        created_at=now,
    )
    snap = SentimentSnapshot(
        symbol="EURUSD",
        score=0.80,
        item_count=3,
        window_hours=24,
        top_drivers=[],
        as_of=now,
        provenance=Provenance(
            sources=["test"],
            generated_at=now,
            model_version=SENTIMENT_MODEL_VERSION,
            confidence=0.6,
        ),
    )
    added: list[object] = []

    class FakeSession:
        def scalar(self, _stmt):
            return prev

        def add(self, obj: object) -> None:
            added.append(obj)

        def flush(self) -> None:
            return None

    row, spiked = persist_sentiment(FakeSession(), snap, enqueue_spike=True)
    assert spiked is True
    assert isinstance(row, SentimentRow)
    assert any(isinstance(o, OutboxMessage) and o.event == "sentiment.spike" for o in added)


def test_aggregate_requires_cached_scores() -> None:
    now = datetime.now(UTC)
    item = NewsItem(
        id=1,
        external_id="agg-1",
        symbol="EURUSD",
        headline="test",
        source="test",
        published_at=now,
    )

    class FakeSession:
        def scalars(self, _stmt):
            return SimpleNamespace(all=lambda: [item])

    # No scores → None
    assert aggregate_symbol_sentiment(FakeSession(), "EURUSD", now=now, scores={}) is None
    snap = aggregate_symbol_sentiment(
        FakeSession(), "EURUSD", now=now, scores={"agg-1": 0.5}
    )
    assert snap is not None
    assert snap.score == pytest.approx(0.5)
    assert snap.schema_id == "sentiment.v1"
