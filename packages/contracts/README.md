# Ouroboros data contracts (v1)

Versioned Pydantic models shared by `server/`, sibling platforms (EPG, quant), and JSON Schema consumers.

| Schema ID | Model | File |
|-----------|-------|------|
| `profile.v1` | `AssetProfile` | `contracts/profile_v1.py` |
| `state.v1` | `MarketState` | `contracts/state_v1.py` |
| `sentiment.v1` | `SentimentSnapshot` | `contracts/sentiment_v1.py` |
| `insight.v1` | `Insight` | `contracts/insight_v1.py` |
| `events.v1.*` | stream event envelopes | `contracts/events_v1.py` |

Shared provenance lives in `contracts/common_v1.py`.

## Install (editable)

```bash
cd packages/contracts
pip install -e .
# or: uv pip install -e .
```

## Export JSON Schema

```bash
cd packages/contracts
python -m contracts.export_jsonschema
```

Outputs land in `contracts/jsonschema/`.

## Rules

- Breaking changes create `v2` modules — never mutate `v1` fields in place.
- Every output carries `provenance` (`sources`, `generated_at`, `model_version`, `confidence`, `stale`).
- `Insight.type` is always `"narrative"` (generative tier only).
