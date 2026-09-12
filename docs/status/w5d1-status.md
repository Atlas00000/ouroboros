# W5·D1 status — daily AssetProfile builder (`profile.v1`)

**Date:** 2026-09-12  
**Models:** `profiles.v1` · `metrics.v1` · `regimes.rule_v1`

## Delivered

- `app/analytics/profiles.py`
  - `build_asset_profile` — assembles identity, D1 volatility/liquidity proxies,
    H1 30d correlations, H1 regime distribution, provenance
  - `build_asset_profile_from_session` — DB orchestration helper
- Tests: `tests/test_profiles.py` (contract round-trip + USDCHF depth gate)
- Smoke: `scripts/smoke_profile_eurusd.py`

## Side fix

`realized_vol` `min_periods` softened (`window - window//5`) so D1 FX series with
weekend-null returns still produce finite vol20/60 (was all-NaN with
`min_periods=window`).

## Smoke (EURUSD, local Docker)

| Field | Result |
| --- | --- |
| schema | `profile.v1` |
| correlations | GBPUSD / XAUUSD / USDJPY (peers capped in smoke) |
| regime shares | from H1 confirmed labels |
| liquidity | range proxy only; true spread deferred |

## Next

**W5·D2** — done; see `docs/status/w5d2-status.md`. Next: **W5·D3** forecast/regime-call log.
