"""MarketState contract — state.v1."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from pydantic import Field, model_validator

from contracts.common_v1 import (
    ContractModel,
    Disclaimer,
    Provenance,
    RegimeLabel,
    Timeframe,
)


class RegimeProbability(ContractModel):
    regime: RegimeLabel
    probability: Annotated[float, Field(ge=0.0, le=1.0)]


class MarketState(ContractModel):
    """Current market state / regime classification (schema_id: state.v1)."""

    schema_id: Annotated[str, Field(pattern="^state\\.v1$")] = "state.v1"
    symbol: str
    timeframe: Timeframe
    regime: RegimeLabel
    regime_probabilities: list[RegimeProbability] = Field(min_length=1)
    volatility_percentile: Annotated[float, Field(ge=0.0, le=100.0)] | None = None
    trend_strength: Annotated[float, Field(ge=-1.0, le=1.0)] | None = Field(
        default=None,
        description="Signed trend strength in [-1, 1]; positive = up.",
    )
    as_of: datetime
    provenance: Provenance
    disclaimer: Disclaimer = Field(default_factory=Disclaimer)

    @model_validator(mode="after")
    def _probabilities_cover_regime(self) -> MarketState:
        labels = {p.regime for p in self.regime_probabilities}
        if self.regime not in labels:
            raise ValueError(f"regime '{self.regime}' missing from regime_probabilities")
        total = sum(p.probability for p in self.regime_probabilities)
        if abs(total - 1.0) > 0.02:
            raise ValueError(f"regime_probabilities must sum to ~1.0, got {total:.4f}")
        return self
