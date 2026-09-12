# W4·D5 status — regression fixtures + Week 4 analytics closeout

**Date:** 2026-09-12  
**Models:** `metrics.v1` · `regimes.rule_v1`

## Delivered

- Regression fixture: `tests/fixtures/analytics/regime_rule_v1.json`
  - Pins tuned params (`vol_high=75`, `er_abs=0.25`, `persistence_n=3`)
  - Grid boundary cases, persistence sequences, soft-probability dominance
- Tests: `tests/test_analytics_regression.py`
  - Fixture-driven regime pins
  - `metrics.v1` snapshot on all TFs (M1/M15/H1/H4/D1)
  - Dataclass field surface lock for profile builders
- Week 4 suite: metrics + correlations + regimes + backtest + regression

## Week 4 rollup

| Day | Outcome |
| --- | --- |
| W4·D1 | M15/H4 caggs; vol/ATR/returns (`metrics.v1`) |
| W4·D2 | Kaufman ER; H1 30d corr; range liquidity; USDCHF depth gate |
| W4·D3 | Rule classifier + soft probs + N=3 hysteresis |
| W4·D4 | Flip-rate tune → defaults 75 / 0.25 / 3; H1 ~0.86 flips/day |
| W4·D5 | Fixtures + full metric TF coverage + this note |

## Next

**W5·D2** — event-triggered profile refresh + versioning + 180d retention (see `docs/status/w5d1-status.md`).
