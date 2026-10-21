# NVDA research dossier

Living asset profile + monthly regime / fit audit produced from the local Ouroboros pipe.

> **Depth:** YWO MT5 `NVDA` history starts 2026-01-14 (≈275d M1). Requested 2y; boards cover available broker depth.

| File | Contents |
| --- | --- |
| [`PROFILE.md`](./PROFILE.md) | Comprehensive asset profile (identity, clocks, character, path, narrative) |
| [`regime-audit.md`](./regime-audit.md) | Monthly H1/D1 regime shares + MATCH/MISMATCH/FRAGILE tags |
| [`profile.json`](./profile.json) | `profile.v1` snapshot |
| [`audit.json`](./audit.json) | Full machine export (boards, nowcast, news) |
| [`BMRG_M15_chart_preset.md`](./BMRG_M15_chart_preset.md) | BMRG M15 ~6m chart preset (Balanced 550/690 + ATR/BBW) |
| [`bmrg_m15_6m_audit.json`](./bmrg_m15_6m_audit.json) | BMRG M15* probe audit export |
| [`bmrg_m15_6m_reprobe.json`](./bmrg_m15_6m_reprobe.json) | Cost/regime re-probe (chosen sleeve) |
| [`BMRG_M5_chart_preset.md`](./BMRG_M5_chart_preset.md) | BMRG M5 ~6m chart preset (Balanced 300/380 + ATR) |
| [`bmrg_m5_6m_audit.json`](./bmrg_m5_6m_audit.json) | BMRG M5* probe audit export |
| [`bmrg_m5_6m_reprobe.json`](./bmrg_m5_6m_reprobe.json) | M5 cost/regime re-probe (chosen sleeve) |

**Canvas covers:**  
- [nvda-asset-profile.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/nvda-asset-profile.canvas.tsx) — asset profile  
- [bmrg-nvda-m15-preset.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/bmrg-nvda-m15-preset.canvas.tsx) — BMRG M15 preset  
- [bmrg-nvda-m5-preset.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/bmrg-nvda-m5-preset.canvas.tsx) — BMRG M5 preset  

Models: `regimes.rule_v1` · `fit.map_v0` · `profiles.v1`  
Range: 2026-01-14 → 2026-10-16 · regenerated via `nvda_regime_audit.py` / `bmrg_nvda_m15_6m_audit.py` / `bmrg_nvda_m5_6m_audit.py`
