"""Insight / narrative contract — insight.v1."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import Field

from contracts.common_v1 import ContractModel, Disclaimer, Provenance


class Insight(ContractModel):
    """LLM-generated narrative built on deterministic outputs (schema_id: insight.v1).

    Generative tier only — never feeds numeric fields consumed by analytics.
    """

    schema_id: Annotated[str, Field(pattern="^insight\\.v1$")] = "insight.v1"
    type: Literal["narrative"] = Field(
        default="narrative",
        description="Always 'narrative' — distinguishes generative from deterministic payloads.",
    )
    symbol: str | None = Field(
        default=None,
        description="Asset symbol when insight is asset-scoped; null for market-wide.",
    )
    title: str
    body: str = Field(description="Readable insight text produced by the generative tier.")
    tags: list[str] = Field(default_factory=list)
    related_refs: list[str] = Field(
        default_factory=list,
        description="IDs/refs of deterministic inputs used (profile/state/sentiment versions).",
    )
    as_of: datetime
    provenance: Provenance
    disclaimer: Disclaimer = Field(default_factory=Disclaimer)
