# W5·D3 status — immutable forecast / regime-call log

**Date:** 2026-09-12  
**Model tag on writes:** `regimes.rule_v1`

## Delivered

- `app/analytics/forecast_log.py`
  - `log_regime_call` / `log_forecast_call` — append-only writers
  - `classify_and_log_regimes` — classify latest H1/H4/D1 (default) + log
  - Prediction JSON includes regime, raw, soft probs, vol/ER, skip flags, as_of
  - Confidence = soft-prob mass on confirmed regime (0 if skipped)
  - Horizon minutes by TF for later scoring (H1=60, H4=240, D1=1440)
- Migration `0007_forecast_log_unique` — idempotent identity  
  `(symbol, timeframe, call_type, made_at, model_version)`
- CLI: `ops/analytics/log_regime_calls.py`
- Smoke: `scripts/smoke_forecast_log.py`
- Tests: `tests/test_forecast_log.py`

## Immutability

- Prediction fields never updated after insert
- Re-runs de-dupe (smoke: 3 insert → 3 dupes)
- `realized_json` / `scored_at` / `score` reserved for W8 scoring job

## Smoke (EURUSD)

| TF | Result |
| --- | --- |
| H1 / H4 / D1 | inserted with `regimes.rule_v1` |
| Re-run | 0 inserted, 3 dupes |

## Next

**W5·D4** — done; see `docs/status/w5d4-status.md`. Next: **W5·D5** HMM spike + ADR.
