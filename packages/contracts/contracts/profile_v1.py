"""AssetProfile contract — profile.v1."""

from __future__ import annotations

from datetime import datetime, time
from typing import Annotated

from pydantic import Field

from contracts.common_v1 import ContractModel, Disclaimer, Provenance, RegimeLabel


class AssetIdentity(ContractModel):
    symbol: str = Field(description="Canonical internal symbol ID, e.g. 'EURUSD'.")
    display_name: str
    asset_class: Annotated[
        str,
        Field(pattern="^(fx|metal|index|equity|crypto|rate|other)$"),
    ]
    venues: list[str] = Field(default_factory=list, description="Trading venues / brokers.")
    mt5_ticker: str | None = Field(default=None, description="Broker-specific MT5 symbol.")
    base_currency: str | None = None
    quote_currency: str | None = None


class TradingHours(ContractModel):
    timezone: str = Field(default="UTC", description="IANA timezone used for session bounds.")
    sessions: list[str] = Field(
        default_factory=list,
        description="Named sessions, e.g. ['sydney', 'tokyo', 'london', 'new_york'].",
    )
    open_utc: time | None = None
    close_utc: time | None = None
    notes: str | None = None


class VolatilityCharacter(ContractModel):
    atr_percentile_30d: Annotated[float, Field(ge=0.0, le=100.0)] | None = None
    realized_vol_percentile_30d: Annotated[float, Field(ge=0.0, le=100.0)] | None = None
    typical_daily_range: float | None = Field(
        default=None,
        description="Typical daily high-low range in price units.",
    )


class LiquidityCharacter(ContractModel):
    typical_spread: float | None = None
    spread_percentile_30d: Annotated[float, Field(ge=0.0, le=100.0)] | None = None
    notes: str | None = None


class CorrelationEntry(ContractModel):
    symbol: str
    coefficient: Annotated[float, Field(ge=-1.0, le=1.0)]
    window_days: int = Field(ge=1, default=30)


class EventSensitivity(ContractModel):
    event_type: str = Field(description="e.g. 'NFP', 'CPI', 'FOMC', 'central_bank'.")
    typical_move_atr_multiple: float | None = None
    notes: str | None = None


class RegimeDistribution(ContractModel):
    regime: RegimeLabel
    share: Annotated[float, Field(ge=0.0, le=1.0)] = Field(
        description="Fraction of sample history spent in this regime.",
    )


class AssetProfile(ContractModel):
    """Living, versioned dossier for one instrument (schema_id: profile.v1)."""

    schema_id: Annotated[str, Field(pattern="^profile\\.v1$")] = "profile.v1"
    profile_version: int = Field(ge=1, description="Monotonic profile generation version.")
    identity: AssetIdentity
    trading_hours: TradingHours = Field(default_factory=TradingHours)
    volatility: VolatilityCharacter = Field(default_factory=VolatilityCharacter)
    liquidity: LiquidityCharacter = Field(default_factory=LiquidityCharacter)
    correlations: list[CorrelationEntry] = Field(default_factory=list)
    event_sensitivities: list[EventSensitivity] = Field(default_factory=list)
    regime_distribution: list[RegimeDistribution] = Field(default_factory=list)
    as_of: datetime = Field(description="UTC as-of for the profile snapshot.")
    provenance: Provenance
    disclaimer: Disclaimer = Field(default_factory=Disclaimer)
