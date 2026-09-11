"""Shared contract primitives for Ouroboros v1 payloads."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class ContractModel(BaseModel):
    """Base for all versioned contracts — ignore unknown fields for forward compat."""

    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class Provenance(ContractModel):
    """Trust metadata required on every Ouroboros output (roadmap F14 / N6)."""

    sources: list[str] = Field(
        default_factory=list,
        description="Upstream data sources or feed IDs that contributed to this output.",
    )
    generated_at: datetime = Field(description="UTC timestamp when this output was produced.")
    model_version: str = Field(
        description="Deterministic or generative model/version string, e.g. 'regimes.rule_v1'.",
    )
    confidence: Annotated[float, Field(ge=0.0, le=1.0)] = Field(
        description="Producer confidence in [0, 1].",
    )
    stale: bool = Field(
        default=False,
        description="True when one or more contributing feeds exceeded cadence expectations.",
    )


class Disclaimer(ContractModel):
    """Advisory disclaimer — research only, not investment advice / not execution."""

    text: str = Field(
        default=(
            "Ouroboros provides internal research context only. "
            "Outputs are not investment advice and do not execute trades."
        ),
    )
    url: HttpUrl | None = None


RegimeLabel = Annotated[
    str,
    Field(
        pattern="^(trending_up|trending_down|ranging|high_volatility)$",
        description="One of: trending_up | trending_down | ranging | high_volatility",
    ),
]

Timeframe = Annotated[
    str,
    Field(
        pattern="^(M1|M5|M15|M30|H1|H4|D1|W1)$",
        description="Bar timeframe code.",
    ),
]
