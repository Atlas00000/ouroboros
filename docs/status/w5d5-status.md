# W5·D5 status — HMM spike vs rule_v1 + Phase 2 analytics closeout

**Date:** 2026-09-12  
**Models:** production `regimes.rule_v1` · spike `regimes.hmm_v1` (not promoted)

## Delivered

- `app/analytics/hmm_regimes.py` — 4-state Gaussian HMM on (vol_pct, ER)
- CLI: `ops/analytics/compare_hmm_regimes.py`
- Optional dep: `pip install 'ouroboros-server[hmm]'`
- Tests: `tests/test_hmm_regimes.py`
- **ADR-017:** keep rule_v1 ([docs/adr/017-keep-rule-regimes-over-hmm.md](../adr/017-keep-rule-regimes-over-hmm.md))
- Summary JSON: `docs/status/w5d5-hmm-summary.json`

## Result (H1, 14 symbols)

| | rule | hmm |
| --- | ---: | ---: |
| avg flips/day | 0.989 | 0.849 |
| within budget | 14/14 | 14/14 |
| avg agreement | — | 0.490 |

**Decision:** `keep_rule_v1` (agreement gate 0.55 not met).

## Phase 2 rollup (W4–W5)

| Day | Outcome |
| --- | --- |
| W4·D1–D5 | metrics.v1, corr, regimes.rule_v1, flip tune, fixtures |
| W5·D1 | AssetProfile builder |
| W5·D2 | Persist + event refresh + 180d retention |
| W5·D3 | Immutable forecast_log |
| W5·D4 | APScheduler worker |
| W5·D5 | HMM spike rejected; ADR-017 |

## Tag

Tagged and pushed: **`v0.3-analytics`** on `d33f4d5`.

## Next

**Phase 3 / W6·D1** — started; see `docs/status/w6d1-status.md`.
