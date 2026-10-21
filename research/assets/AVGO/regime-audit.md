# AVGO — Regime audit & fit tagging (monthly)

> Ex-post calendar-month boards · `regimes.rule_v1` labels → `fit.map_v0`  
> Window: 2026-02 → 2026-10 (8 H1 months with confirmed bars after warmup)

> Broker depth: YWO `Broadcom` M1 starts `2026-02-26` (≈225d). Full 2y not available from this feed.

## Method

1. Load H1 / D1 OHLCV (~800d lookback request; broker depth binds).
2. Run `regime_feature_frame` → confirmed regime per bar.
3. Slice each calendar month; map regimes → MATCH / MISMATCH / FRAGILE per edge family.
4. Dominant tag = largest fit-share (ties break MISMATCH > FRAGILE > MATCH).

Families: **meanrev** home=`ranging`; **trendfollow** home=`trending_up|trending_down`; both treat `high_volatility` as FRAGILE.

## Tag summary (months with bars)

| TF × family | MATCH | MISMATCH | FRAGILE |
| --- | ---: | ---: | ---: |
| `H1|meanrev` | 5 | 2 | 1 |
| `H1|trendfollow` | 2 | 5 | 1 |
| `D1|meanrev` | 4 | 1 | 3 |
| `D1|trendfollow` | 1 | 4 | 3 |

Dominant-regime months (H1): {'ranging': 6, 'trending_up': 1, 'high_volatility': 1}
Dominant-regime months (D1): {'high_volatility': 3, 'ranging': 4, 'trending_down': 1}

## H1 monthly board

| Month | Dominant regime | meanrev | trendfollow | Bars | ranging | trend↑ | trend↓ | high_vol |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2026-03 | ranging | **MATCH** | **MISMATCH** | 2 | 100.0% | 0.0% | 0.0% | 0.0% |
| 2026-04 | trending_up | **MISMATCH** | **MATCH** | 140 | 22.1% | 55.7% | 10.0% | 12.1% |
| 2026-05 | ranging | **MATCH** | **MISMATCH** | 140 | 55.7% | 15.0% | 5.0% | 24.3% |
| 2026-06 | high_volatility | **FRAGILE** | **FRAGILE** | 147 | 27.2% | 2.0% | 6.1% | 64.6% |
| 2026-07 | ranging | **MATCH** | **MISMATCH** | 154 | 56.5% | 9.7% | 12.3% | 21.4% |
| 2026-08 | ranging | **MISMATCH** | **MATCH** | 147 | 34.7% | 24.5% | 34.7% | 6.1% |
| 2026-09 | ranging | **MATCH** | **MISMATCH** | 147 | 54.4% | 14.3% | 27.2% | 4.1% |
| 2026-10 | ranging | **MATCH** | **MISMATCH** | 49 | 51.0% | 32.7% | 10.2% | 6.1% |

## D1 monthly board

| Month | Dominant regime | meanrev | trendfollow | Bars | ranging | trend↑ | trend↓ | high_vol |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2026-03 | high_volatility | **FRAGILE** | **FRAGILE** | 1 | 0.0% | 0.0% | 0.0% | 100.0% |
| 2026-04 | high_volatility | **FRAGILE** | **FRAGILE** | 20 | 0.0% | 45.0% | 0.0% | 55.0% |
| 2026-05 | ranging | **MATCH** | **MISMATCH** | 20 | 55.0% | 45.0% | 0.0% | 0.0% |
| 2026-06 | high_volatility | **FRAGILE** | **FRAGILE** | 21 | 23.8% | 0.0% | 0.0% | 76.2% |
| 2026-07 | ranging | **MATCH** | **MISMATCH** | 22 | 81.8% | 0.0% | 0.0% | 18.2% |
| 2026-08 | ranging | **MATCH** | **MISMATCH** | 21 | 100.0% | 0.0% | 0.0% | 0.0% |
| 2026-09 | trending_down | **MISMATCH** | **MATCH** | 21 | 47.6% | 0.0% | 52.4% | 0.0% |
| 2026-10 | ranging | **MATCH** | **MISMATCH** | 7 | 100.0% | 0.0% | 0.0% | 0.0% |

## Audit takeaways

1. **H1 meanrev MATCH in 5/8 months** vs trendfollow MATCH in 2/8 — modal H1 month regime is **ranging** (6/8).
2. **Fragile months:** 2026-06 (high_vol-dominant → both families FRAGILE).
3. **Trendfollow MATCH months:** 2026-04, 2026-08 (ex-post; not forward signals).
4. **Live gate vs character:** nowcast can lean trending_up while history clock stays ranging-led — use 30d shares for the research gate.
5. **Partial months:** early/late months may have few confirmed bars after regime warmup (e.g. Mar / Oct).
6. Monthly MATCH is **ex-post**, not a forward signal. Live research gate should use nowcast + 30d shares, not calendar-month prophecy.

Research / advisory only. Ex-post monthly MATCH boards are not profit claims. fit.map_v0 gates research books — not execution.
