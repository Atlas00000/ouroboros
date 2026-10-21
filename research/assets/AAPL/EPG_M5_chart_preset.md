# EPG · AAPL · M5 — Balanced chart preset

**Status:** research / untested in MT5  
**Sleeve:** Balanced (functional WR + returns)  
**Framework:** `docs/framework/unified_edge_framework.md`  
**Hard rule:** never emit TP < SL · DesignedRR = **2.0** (SL 150 / TP 300 points)

## Tip window (~6m)

| Field | Value |
| --- | --- |
| Data | M5* from M1 · 2026-05-01 → 2026-10-07 |
| ATR med | ~$0.63 (~63 pts @ Point=0.01) |
| H1 trendfollow | **MISMATCH** (range-led) |
| H1 meanrev | **MATCH** |
| Audit | `epg_m5_6m_audit.json` |

## Recommended geometry

| Knob | Value | Role |
| --- | --- | --- |
| Chart TF | M5 | denser pullbacks than M15 |
| L1 ATR | **1.0** | Balanced depth (not ultra-deep) |
| MaxLevels | 1 | single decision / basket |
| SL / TP | **150 / 300** | RR **2.0**, TP > SL |
| BasketTP$ | 0 | hard TP is the win path |
| Session | **13–20** UTC | US cash sleeve |
| Cooldown | 3600s | ~12 M5 bars |
| Lot | 1.0 | Apple min volume |
| Magic | 26101951 | |

### Probe Stage 0

| n | WR | BWR | E_N | RR_design |
| ---: | ---: | ---: | ---: | ---: |
| 105 | 41.0% | 38.9% | **+0.053R** | 2.0 |

Native dual-TF gate blocked ~2.2k FLAT bars — that is the regime filter. Optional confirmed H1 trend gate shrinks n hard on this tip; keep OFF unless re-probed.

## Preset path

`MQL5/Profiles/Tester/EPG/AAPL/EPG-M5-AAPL-6M-Balanced_RR2.0.set`  
Script: `server/scripts/epg_aapl_m5_6m_audit.py`
