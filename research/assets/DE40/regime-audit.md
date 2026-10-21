# DE40 — Regime audit & fit tagging (monthly)

> Ex-post calendar-month boards · `regimes.rule_v1` labels → `fit.map_v0`  
> Window: 2025-06 → 2026-10 (17 H1 months with confirmed bars after warmup)

> Broker depth: YWO `DE40`/`DE30` M1 starts `2025-06-05` (≈489d). Full 2y not available from this feed.

## Method

1. Load H1 / D1 OHLCV (~800d lookback request; broker depth binds).
2. Run `regime_feature_frame` → confirmed regime per bar.
3. Slice each calendar month; map regimes → MATCH / MISMATCH / FRAGILE per edge family.
4. Dominant tag = largest fit-share (ties break MISMATCH > FRAGILE > MATCH).

Families: **meanrev** home=`ranging`; **trendfollow** home=`trending_up|trending_down`; both treat `high_volatility` as FRAGILE.

## Tag summary (months with bars)

| TF × family | MATCH | MISMATCH | FRAGILE |
| --- | ---: | ---: | ---: |
| `H1|meanrev` | 10 | 3 | 4 |
| `H1|trendfollow` | 3 | 10 | 4 |
| `D1|meanrev` | 5 | 4 | 7 |
| `D1|trendfollow` | 4 | 5 | 7 |

Dominant-regime months (H1): {'high_volatility': 5, 'ranging': 12}
Dominant-regime months (D1): {'high_volatility': 7, 'ranging': 5, 'trending_down': 1, 'trending_up': 3}

## H1 monthly board

| Month | Dominant regime | meanrev | trendfollow | Bars | ranging | trend↑ | trend↓ | high_vol |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2025-06 | high_volatility | **MISMATCH** | **MATCH** | 229 | 25.3% | 24.9% | 20.5% | 29.3% |
| 2025-07 | ranging | **MISMATCH** | **MATCH** | 528 | 31.6% | 29.7% | 27.3% | 11.4% |
| 2025-08 | ranging | **MATCH** | **MISMATCH** | 483 | 64.6% | 11.6% | 7.5% | 16.4% |
| 2025-09 | ranging | **MATCH** | **MISMATCH** | 505 | 44.2% | 18.4% | 7.1% | 30.3% |
| 2025-10 | ranging | **MATCH** | **MISMATCH** | 522 | 47.5% | 14.9% | 11.7% | 25.9% |
| 2025-11 | high_volatility | **FRAGILE** | **FRAGILE** | 460 | 22.6% | 22.2% | 4.8% | 50.4% |
| 2025-12 | ranging | **MATCH** | **MISMATCH** | 433 | 60.5% | 28.9% | 10.6% | 0.0% |
| 2026-01 | ranging | **MATCH** | **MISMATCH** | 482 | 45.2% | 18.9% | 4.1% | 31.7% |
| 2026-02 | ranging | **MATCH** | **MISMATCH** | 459 | 40.5% | 23.5% | 7.6% | 28.3% |
| 2026-03 | high_volatility | **FRAGILE** | **FRAGILE** | 508 | 18.9% | 7.1% | 9.6% | 64.4% |
| 2026-04 | ranging | **MATCH** | **MISMATCH** | 455 | 60.4% | 16.3% | 13.0% | 10.3% |
| 2026-05 | ranging | **MISMATCH** | **MATCH** | 460 | 40.4% | 25.0% | 20.4% | 14.1% |
| 2026-06 | ranging | **MATCH** | **MISMATCH** | 505 | 49.9% | 10.5% | 18.6% | 21.0% |
| 2026-07 | ranging | **MATCH** | **MISMATCH** | 527 | 49.1% | 17.1% | 12.1% | 21.6% |
| 2026-08 | ranging | **MATCH** | **MISMATCH** | 485 | 67.2% | 21.2% | 11.5% | 0.0% |
| 2026-09 | high_volatility | **FRAGILE** | **FRAGILE** | 503 | 31.0% | 11.7% | 11.3% | 45.9% |
| 2026-10 | high_volatility | **FRAGILE** | **FRAGILE** | 107 | 15.0% | 10.3% | 8.4% | 66.4% |

## D1 monthly board

| Month | Dominant regime | meanrev | trendfollow | Bars | ranging | trend↑ | trend↓ | high_vol |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2025-07 | high_volatility | **FRAGILE** | **FRAGILE** | 23 | 34.8% | 0.0% | 0.0% | 65.2% |
| 2025-08 | ranging | **MATCH** | **MISMATCH** | 26 | 53.8% | 0.0% | 0.0% | 46.2% |
| 2025-09 | trending_down | **MISMATCH** | **MATCH** | 26 | 26.9% | 0.0% | 42.3% | 30.8% |
| 2025-10 | high_volatility | **FRAGILE** | **FRAGILE** | 27 | 29.6% | 0.0% | 0.0% | 70.4% |
| 2025-11 | ranging | **MATCH** | **MISMATCH** | 25 | 72.0% | 0.0% | 0.0% | 28.0% |
| 2025-12 | trending_up | **MISMATCH** | **MATCH** | 22 | 27.3% | 54.5% | 0.0% | 18.2% |
| 2026-01 | trending_up | **MISMATCH** | **MATCH** | 25 | 0.0% | 72.0% | 0.0% | 28.0% |
| 2026-02 | high_volatility | **FRAGILE** | **FRAGILE** | 24 | 12.5% | 0.0% | 0.0% | 87.5% |
| 2026-03 | high_volatility | **FRAGILE** | **FRAGILE** | 27 | 14.8% | 0.0% | 0.0% | 85.2% |
| 2026-04 | high_volatility | **FRAGILE** | **FRAGILE** | 23 | 4.3% | 43.5% | 0.0% | 52.2% |
| 2026-05 | ranging | **MATCH** | **MISMATCH** | 24 | 100.0% | 0.0% | 0.0% | 0.0% |
| 2026-06 | ranging | **MATCH** | **MISMATCH** | 26 | 100.0% | 0.0% | 0.0% | 0.0% |
| 2026-07 | ranging | **MATCH** | **MISMATCH** | 27 | 88.9% | 11.1% | 0.0% | 0.0% |
| 2026-08 | trending_up | **MISMATCH** | **MATCH** | 26 | 34.6% | 65.4% | 0.0% | 0.0% |
| 2026-09 | high_volatility | **FRAGILE** | **FRAGILE** | 26 | 38.5% | 0.0% | 0.0% | 61.5% |
| 2026-10 | high_volatility | **FRAGILE** | **FRAGILE** | 6 | 0.0% | 0.0% | 0.0% | 100.0% |

## Audit takeaways

1. **H1 meanrev MATCH in 10/17 months** vs trendfollow MATCH in 3/17 — modal H1 month regime is **ranging** (12/17).
2. **Fragile months:** 2025-11, 2026-03, 2026-09, 2026-10 (high_vol-dominant → both families FRAGILE).
3. **Trendfollow MATCH months:** 2025-06, 2025-07, 2026-05 (ex-post; not forward signals).
4. **Live gate vs character:** nowcast can lean trending_up while history clock stays ranging-led — use 30d shares for the research gate.
5. **Partial months:** early/late months may have few confirmed bars after regime warmup (e.g. first / last month).
6. Monthly MATCH is **ex-post**, not a forward signal. Live research gate should use nowcast + 30d shares, not calendar-month prophecy.

Research / advisory only. Ex-post monthly MATCH boards are not profit claims. fit.map_v0 gates research books — not execution.
