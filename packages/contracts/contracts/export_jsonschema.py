"""Export Pydantic contracts to JSON Schema files under contracts/jsonschema/."""

from __future__ import annotations

import json
from pathlib import Path

from contracts.events_v1 import (
    NewsHighImpactEvent,
    ProfileUpdatedEvent,
    RegimeChangedEvent,
    SentimentSpikeEvent,
)
from contracts.insight_v1 import Insight
from contracts.profile_v1 import AssetProfile
from contracts.sentiment_v1 import SentimentSnapshot
from contracts.state_v1 import MarketState

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "jsonschema"

MODELS: dict[str, type] = {
    "profile.v1": AssetProfile,
    "state.v1": MarketState,
    "sentiment.v1": SentimentSnapshot,
    "insight.v1": Insight,
    "events.v1.regime_changed": RegimeChangedEvent,
    "events.v1.sentiment_spike": SentimentSpikeEvent,
    "events.v1.news_high_impact": NewsHighImpactEvent,
    "events.v1.profile_updated": ProfileUpdatedEvent,
}


def export_all() -> list[Path]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for name, model in MODELS.items():
        path = OUT_DIR / f"{name}.json"
        schema = model.model_json_schema()
        path.write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        written.append(path)
        print(f"wrote {path.relative_to(ROOT.parent)}")
    return written


if __name__ == "__main__":
    export_all()
