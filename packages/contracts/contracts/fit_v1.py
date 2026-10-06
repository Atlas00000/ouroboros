"""FitSnapshot contract — fit.v1 (regime fit tags)."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import Field

from contracts.common_v1 import ContractModel, Disclaimer, Provenance, RegimeLabel, Timeframe

FitTag = Literal["MATCH", "MISMATCH", "FRAGILE"]
EdgeFamily = Literal["meanrev", "trendfollow"]


class FitSnapshot(ContractModel):
    """Regime fit for symbol × timeframe × edge family (schema_id: fit.v1)."""

    schema_id: Annotated[str, Field(pattern="^fit\\.v1$")] = "fit.v1"
    symbol: str
    timeframe: Timeframe
    family: EdgeFamily
    tag: FitTag
    regime: RegimeLabel | None = None
    allow_on: bool = Field(
        description="Research gate: True only when tag == MATCH (v0).",
    )
    shares: dict[str, float] | None = Field(
        default=None,
        description="Optional ex-post fit tag shares over window.",
    )
    window: str | None = Field(
        default=None,
        description="Board window when shares present (7d|30d|calendar_month).",
    )
    fragile_reasons: list[str] = Field(default_factory=list)
    as_of: datetime
    provenance: Provenance
    disclaimer: Disclaimer = Field(default_factory=Disclaimer)
