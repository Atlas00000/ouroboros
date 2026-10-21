# BMRG M15 chart preset — XBRUSD pointer

Emitted 2026-10-12 from Ouroboros XBRUSD ~6m context + M15* FIXED_RR probe + ATR-cap ablation.

| Artifact | Path |
| --- | --- |
| Tester folder (canonical) | `…/MQL5/Profiles/Tester/BMRG/XBRUSD/` |
| Chart / Inputs `.set` | `…/MQL5/Experts/BMRG/Presets/BMRG-M15-XBRUSD-6M-P0_balanced_chart.set` |
| Geometry card | `…/MQL5/Profiles/Tester/BMRG/XBRUSD/BMRG_M15_XBRUSD_6M_chart_preset.md` |
| Machine audit | [`bmrg_m15_6m_audit.json`](./bmrg_m15_6m_audit.json) |
| Framework | [`docs/framework/unified_edge_framework.md`](../../../docs/framework/unified_edge_framework.md) |

**Geometry:** SL **250** / TP **310** · **RR = 1.24** · never TP &lt; SL · session 12–20 · skip Tue · BBDev 2.2 · G0 · AOS off.

| Sleeve | Magic | Delta | Status |
| --- | ---: | --- | --- |
| P0 | 26101220 | ATR≤70 (audit) | ZERO TRADES |
| P0b | 26101221 | ATR≤525 native · both sides | FAIL — sell fake fades |
| **P1** | **26101222** | P0b · **buy only** | **NEXT** |

**Scale note:** audit ATR pts ~10× too small vs Tester/BRENT — use EA-native p75 for ATR max.

Load P1: `BMRG-M15-XBRUSD-6M-P1_buyOnly_chart.set`

**Canvas cover:** `canvases/bmrg-xbrusd-m15-preset.canvas.tsx`
