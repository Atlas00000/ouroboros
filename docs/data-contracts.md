# Data contracts (human summary)

Source of truth: `packages/contracts`. See also [ADR-015](./adr/015-dual-auth-clerk-and-api-keys.md) for auth (orthogonal to these payloads).

## Provenance (every output)

| Field | Meaning |
|-------|---------|
| `sources[]` | Feeds / inputs used |
| `generated_at` | UTC production time |
| `model_version` | e.g. `regimes.rule_v1` |
| `confidence` | 0–1 |
| `stale` | True if a contributing feed missed cadence |

## Regimes

`trending_up` · `trending_down` · `ranging` · `high_volatility`

## Events (Redis Streams)

`regime.changed` · `sentiment.spike` · `news.high_impact` · `profile.updated`

Export machine-readable schemas:

```bash
python -m contracts.export_jsonschema
```
