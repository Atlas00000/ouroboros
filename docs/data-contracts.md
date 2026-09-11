# Data contracts (human summary)

Source of truth: `packages/contracts`. See also [ADR-015](./adr/015-dual-auth-clerk-and-api-keys.md) for auth (orthogonal to these payloads).

## Status — v1 finalized (W1·D3)

Contract review for EPG / quant consumers:

| Consumer need | Covered by |
|---------------|------------|
| On-demand asset dossier | `profile.v1` |
| Live regime / state | `state.v1` + `regime.changed` |
| News context | `sentiment.v1` + `news.high_impact` / `sentiment.spike` |
| Readable research copy | `insight.v1` (`type: narrative` only) |
| Catch-up after disconnect | Redis Streams + event envelopes (`events.v1.*`) |
| Trust / freshness | `provenance` on every payload (`stale`, `confidence`, `model_version`) |

**Frozen for v1:** field names and `schema_id` values. Additive optional fields only via careful expand; breaking changes require `*.v2`.
Metrics time-series payloads stay out of contracts for now (served as API DTOs later) — profiles/states already carry the summary numbers consumers need.

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
