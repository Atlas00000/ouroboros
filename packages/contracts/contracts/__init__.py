"""Ouroboros shared data contracts (v1)."""

from contracts.common_v1 import Disclaimer, Provenance, RegimeLabel, Timeframe
from contracts.events_v1 import (
    EventName,
    NewsHighImpactEvent,
    ProfileUpdatedEvent,
    RegimeChangedEvent,
    SentimentSpikeEvent,
)
from contracts.insight_v1 import Insight
from contracts.profile_v1 import AssetProfile
from contracts.sentiment_v1 import SentimentSnapshot
from contracts.state_v1 import MarketState

__version__ = "0.1.0"

__all__ = [
    "AssetProfile",
    "Disclaimer",
    "EventName",
    "Insight",
    "MarketState",
    "NewsHighImpactEvent",
    "ProfileUpdatedEvent",
    "Provenance",
    "RegimeChangedEvent",
    "RegimeLabel",
    "SentimentSnapshot",
    "SentimentSpikeEvent",
    "Timeframe",
    "__version__",
]
