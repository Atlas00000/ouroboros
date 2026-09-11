"""Redis Streams / outbox event payloads — events.v1."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import Field

from contracts.common_v1 import ContractModel, Provenance, RegimeLabel, Timeframe


EventName = Literal[
    "regime.changed",
    "sentiment.spike",
    "news.high_impact",
    "profile.updated",
]


class EventEnvelope(ContractModel):
    """Common envelope for durable stream events (schema_id: events.v1)."""

    schema_id: Annotated[str, Field(pattern="^events\\.v1$")] = "events.v1"
    event_id: str = Field(description="Unique event id (UUID recommended).")
    event: EventName
    occurred_at: datetime = Field(description="UTC time the domain change occurred.")
    symbol: str | None = None
    provenance: Provenance


class RegimeChangedPayload(ContractModel):
    symbol: str
    timeframe: Timeframe
    previous_regime: RegimeLabel | None = None
    new_regime: RegimeLabel
    as_of: datetime


class SentimentSpikePayload(ContractModel):
    symbol: str
    previous_score: Annotated[float, Field(ge=-1.0, le=1.0)] | None = None
    score: Annotated[float, Field(ge=-1.0, le=1.0)]
    delta: float = Field(description="score - previous_score (or absolute if no previous).")
    as_of: datetime


class NewsHighImpactPayload(ContractModel):
    symbol: str | None = None
    headline: str
    event_type: str | None = Field(default=None, description="e.g. NFP, CPI, FOMC.")
    impact: Literal["high"] = "high"
    scheduled_at: datetime | None = None
    published_at: datetime | None = None
    source: str | None = None


class ProfileUpdatedPayload(ContractModel):
    symbol: str
    profile_version: int = Field(ge=1)
    as_of: datetime


class RegimeChangedEvent(EventEnvelope):
    event: Literal["regime.changed"] = "regime.changed"
    payload: RegimeChangedPayload


class SentimentSpikeEvent(EventEnvelope):
    event: Literal["sentiment.spike"] = "sentiment.spike"
    payload: SentimentSpikePayload


class NewsHighImpactEvent(EventEnvelope):
    event: Literal["news.high_impact"] = "news.high_impact"
    payload: NewsHighImpactPayload


class ProfileUpdatedEvent(EventEnvelope):
    event: Literal["profile.updated"] = "profile.updated"
    payload: ProfileUpdatedPayload
