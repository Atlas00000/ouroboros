# W4·D4 status — regime flip-rate backtest & threshold tune

**Date:** 2026-09-12  
**Model:** `regimes.rule_v1`

## Budgets

| TF | Budget | Result (tuned) |
| --- | --- | --- |
| H1 | ≤ 2 flips / symbol / day | **avg 0.86 / day** — all 14 eligible symbols OK |
| D1 | ≤ 1 flip / symbol / week | **within budget** (NAS100 ~0.06/week; FX D1 sparse after gap filter) |

## Tuned params (adopted as defaults)

| Knob | v0 | Tuned |
| --- | --- | --- |
| `vol_high` | 80 | **75** |
| `er_abs` | 0.30 | **0.25** |
| `persistence_n` | 3 | **3** |

Selection rule: feasible on both budgets, minimize mean ranging share (~0.29).

USDCHF excluded via depth gate (~0.9d M1).

## Tooling

- `app/analytics/backtest.py` — flip-rate measure + grid tune (feature precompute)
- `ops/analytics/backtest_regimes.py` — CLI (`--tune`, `--lookback-days`)

```powershell
py -3.12 ops/analytics/backtest_regimes.py --lookback-days 400 --tune
```

## Follow-ups

- W4·D5: regression fixtures pinning tuned grid + full metrics unit suite status note
- D1 FX gap policy: multiplier raised to 5d; re-check D1 label density after next soak
