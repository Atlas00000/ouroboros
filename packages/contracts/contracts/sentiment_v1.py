"""SentimentSnapshot contract — sentiment.v1."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from pydantic import Field, HttpUrl

from contracts.common_v1 import ContractModel, Disclaimer, Provenance


class SentimentDriver(ContractModel):
    """A headline / article contributing to the score."""

    title: str
    url: HttpUrl | None = None
    published_at: datetime | None = None
    contribution: Annotated[float, Field(ge=-1.0, le=1.0)] | None = Field(
        default=None,
        description="Signed contribution of this item toward the aggregate score.",
    )
    source: str | None = None


class SentimentSnapshot(ContractModel):
    """Decay-weighted 24h sentiment for one asset (schema_id: sentiment.v1)."""

    schema_id: Annotated[str, Field(pattern="^sentiment\\.v1$")] = "sentiment.v1"
    symbol: str
    score: Annotated[float, Field(ge=-1.0, le=1.0)] = Field(
        description="Aggregate sentiment in [-1, +1].",
    )
    item_count: int = Field(ge=0, description="Number of underlying news/calendar items.")
    window_hours: Annotated[int, Field(ge=1)] = Field(
        default=24,
        description="Decay window in hours (default 24).",
    )
    top_drivers: list[SentimentDriver] = Field(default_factory=list)
    as_of: datetime
    provenance: Provenance
    disclaimer: Disclaimer = Field(default_factory=Disclaimer)
