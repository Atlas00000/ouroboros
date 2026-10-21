# BMRG M5 chart preset — XBRUSD pointer

Emitted 2026-10-19 from Ouroboros XBRUSD ~6m M5* probe + buy-only / ATR ablation.

| Artifact | Path |
| --- | --- |
| Tester folder (canonical) | `…/MQL5/Profiles/Tester/BMRG/XBRUSD/` |
| Chart / Inputs `.set` | `…/MQL5/Experts/BMRG/Presets/BMRG-M5-XBRUSD-6M-P0_buyOnly_balanced.set` |
| Geometry card | `…/MQL5/Profiles/Tester/BMRG/XBRUSD/BMRG_M5_XBRUSD_6M_chart_preset.md` |
| Machine audits | [`bmrg_m5_6m_audit.json`](./bmrg_m5_6m_audit.json) · [`bmrg_m5_buyonly_ablation.json`](./bmrg_m5_buyonly_ablation.json) |
| Framework | [`docs/framework/unified_edge_framework.md`](../../../docs/framework/unified_edge_framework.md) |

**Geometry:** SL **390** / TP **490** · **RR = 1.256** · never TP &lt; SL · BBDev **2.5** · session 12–20 · skip Tue · ATR max **315** (native p90) · **sell OFF** · G0 · AOS off · magic **26101950**.

**Probe (design prior):** n≈74 · WR≈56.8% · BWR 44.3% · E_N ≈ +0.28R · EF ≈ +7.9pp (40pt RT Leak). RESEARCH / UNTESTED.

**Why buy-only:** both-sides M5 fades sit at the frontier after Leak; sells drag (same lesson as M15 P0b/P1). ATR uses Digits=3 Point=0.001 — not legacy Point=0.01.

**Canvas cover:** `canvases/bmrg-xbrusd-m5-preset.canvas.tsx`
