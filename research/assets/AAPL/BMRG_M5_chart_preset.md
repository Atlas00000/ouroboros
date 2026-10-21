# BMRG · AAPL · M5 — Balanced chart preset

**Status:** research / untested in MT5  
**Sleeve:** Balanced (functional WR + returns)  
**Framework:** `docs/framework/unified_edge_framework.md`  
**Hard rule:** never emit TP < SL · DesignedRR ≈ **1.47** (SL 190 / TP 280)

## Tip window (~6m)

| Field | Value |
| --- | --- |
| Data | M5* from M1 · 2026-05-01 → 2026-10-07 |
| ATR med | ~63 pts @ Point=0.01 |
| H1 meanrev | **MATCH** (May MISMATCH; Jun FRAGILE share high) |
| Audit | `bmrg_m5_6m_audit.json` |

## Recommended geometry

| Knob | Value | Role |
| --- | --- | --- |
| Chart TF | M5 | denser fades than M15 |
| BB | 20 / **2.5σ** | Stage-1 clear |
| SL / TP | **190 / 280** | RR **≈1.47**, TP > SL |
| ATR gate | **24–98** | regime / HV filter |
| BB-width | 0.30–2.00% | light sleeve |
| Session | **14–20** | US cash |
| Skip Tue | true | weekday cut |
| Cooldown | 6 bars | ≈30m |
| Lot | 1.0 | Apple min volume |
| Magic | 26102011 | |

### Probe Stage 0–1 (design prior)

| n | WR | BWR | EF | E_N | RR_design |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 100 | 51.0% | ~40.4% | **+2.1pp** | **+0.26R** | ≈1.47 |

## Preset path

`MQL5/Profiles/Tester/BMRG/AAPL/BMRG-M5-AAPL-6M-Balanced_TPgtSL.set`  
Script: `server/scripts/bmrg_aapl_m5_6m_audit.py`
