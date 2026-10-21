# META research dossier

Living asset profile + monthly regime / fit audit produced from the local Ouroboros pipe.

> **Depth:** YWO MT5 `Meta` history starts 2026-07-06 (≈95d M1). Requested 2y; boards cover available broker depth.

| File | Contents |
| --- | --- |
| [`PROFILE.md`](./PROFILE.md) | Comprehensive asset profile (identity, clocks, character, path, narrative) |
| [`regime-audit.md`](./regime-audit.md) | Monthly H1/D1 regime shares + MATCH/MISMATCH/FRAGILE tags |
| [`profile.json`](./profile.json) | `profile.v1` snapshot |
| [`audit.json`](./audit.json) | Full machine export (boards, nowcast, news) |
| [`BMRG_M15_chart_preset.md`](./BMRG_M15_chart_preset.md) | BMRG M15 chart/Tester preset pointer |
| [`bmrg_m15_6m_audit.json`](./bmrg_m15_6m_audit.json) | M15* geometry probe + meanrev monthly tip |

**Canvas cover:** [meta-asset-profile.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/meta-asset-profile.canvas.tsx) — open beside chat.

**BMRG Tester (P2 — use these):** `…/MQL5/Profiles/Tester/BMRG/META/`  
- Harvest WR: `BMRG-M15-META-6M-P2_harvest_WRfocus.set` (1000/1000 · session 14:00 · magic **26101217**)  
- Balanced TP&gt;SL: `BMRG-M15-META-6M-P2_balanced_TPgtSL.set` (1000/1500 · session 14:00 · magic **26101218**)

Models: `regimes.rule_v1` · `fit.map_v0` · `profiles.v1`  
Range: 2026-07-06 → 2026-10-09 · regenerated via `server/scripts/meta_regime_audit.py` · BMRG via `bmrg_meta_m15_6m_audit.py`
