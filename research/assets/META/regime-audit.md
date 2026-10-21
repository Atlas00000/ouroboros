# META — Regime audit & fit tagging (monthly)

> Ex-post calendar-month boards · `regimes.rule_v1` labels → `fit.map_v0`  
> Window: 2026-07 → 2026-10 (3 H1 months with confirmed bars after warmup)

> Broker depth: YWO `Meta` M1 starts `2026-07-06` (≈95d). Full 2y not available from this feed.

## Method

1. Load H1 / D1 OHLCV (~800d lookback request; broker depth binds).
2. Run `regime_feature_frame` → confirmed regime per bar.
3. Slice each calendar month; map regimes → MATCH / MISMATCH / FRAGILE per edge family.
4. Dominant tag = largest fit-share (ties break MISMATCH > FRAGILE > MATCH).

Families: **meanrev** home=`ranging`; **trendfollow** home=`trending_up|trending_down`; both treat `high_volatility` as FRAGILE.

## Tag summary (months with bars)

| TF × family | MATCH | MISMATCH | FRAGILE |
| --- | ---: | ---: | ---: |
| `H1|meanrev` | 2 | 1 | 0 |
| `H1|trendfollow` | 1 | 2 | 0 |
| `D1|meanrev` | 1 | 1 | 1 |
| `D1|trendfollow` | 1 | 1 | 1 |

Dominant-regime months (H1): {'ranging': 2, 'trending_up': 1}
Dominant-regime months (D1): {'trending_down': 1, 'ranging': 1, 'high_volatility': 1}

## H1 monthly board

| Month | Dominant regime | meanrev | trendfollow | Bars | ranging | trend↑ | trend↓ | high_vol |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2026-08 | ranging | **MATCH** | **MISMATCH** | 124 | 58.9% | 13.7% | 16.9% | 10.5% |
| 2026-09 | trending_up | **MISMATCH** | **MATCH** | 147 | 34.0% | 38.1% | 8.8% | 19.0% |
| 2026-10 | ranging | **MATCH** | **MISMATCH** | 49 | 57.1% | 16.3% | 26.5% | 0.0% |

## D1 monthly board

| Month | Dominant regime | meanrev | trendfollow | Bars | ranging | trend↑ | trend↓ | high_vol |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2026-08 | trending_down | **MISMATCH** | **MATCH** | 15 | 33.3% | 0.0% | 66.7% | 0.0% |
| 2026-09 | ranging | **MATCH** | **MISMATCH** | 21 | 38.1% | 33.3% | 0.0% | 28.6% |
| 2026-10 | high_volatility | **FRAGILE** | **FRAGILE** | 7 | 0.0% | 0.0% | 0.0% | 100.0% |

## Audit takeaways

1. **H1 meanrev MATCH in 2/3 months** vs trendfollow MATCH in 1/3 — modal H1 month regime is **ranging** (2/3).
2. **Fragile months:** none in the confirmed H1 board.
3. **Trendfollow MATCH months:** 2026-09 (ex-post; not forward signals).
4. **Live gate vs character:** soft nowcast mass can lean ranging while confirmed label flips (low confidence) — use 30d shares for the research gate.
5. **Partial months:** Jul warmup and Oct partial month may have few confirmed bars after regime warmup.
6. Monthly MATCH is **ex-post**, not a forward signal. Live research gate should use nowcast + 30d shares, not calendar-month prophecy.

Research / advisory only. Ex-post monthly MATCH boards are not profit claims. fit.map_v0 gates research books — not execution.
