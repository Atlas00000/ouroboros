# UK100 research dossier

Living asset profile + monthly regime / fit audit produced from the local Ouroboros pipe.

> **Depth:** YWO MT5 `UK100` history starts 2025-12-17 (≈298d M1). Requested 2y; boards cover available broker depth.

| File | Contents |
| --- | --- |
| [`PROFILE.md`](./PROFILE.md) | Comprehensive asset profile (identity, clocks, character, path, narrative) |
| [`regime-audit.md`](./regime-audit.md) | Monthly H1/D1 regime shares + MATCH/MISMATCH/FRAGILE tags |
| [`profile.json`](./profile.json) | `profile.v1` snapshot |
| [`audit.json`](./audit.json) | Full machine export (boards, nowcast, news) |
| [`bmrg_m15_6m_audit.json`](./bmrg_m15_6m_audit.json) | BMRG M15* ~6m geometry probe (framework Stage 0–1) |
| [`bmrg_m5_6m_audit.json`](./bmrg_m5_6m_audit.json) | BMRG M5* ~6m geometry probe |
| [`BMRG_M15_chart_preset.md`](./BMRG_M15_chart_preset.md) | BMRG M15 chart/tester preset card |
| [`BMRG_M5_chart_preset.md`](./BMRG_M5_chart_preset.md) | BMRG M5 chart/tester preset card |

**Canvas cover:** [uk100-asset-profile.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/uk100-asset-profile.canvas.tsx) — open beside chat.

**BMRG M5 tester preset:** `Profiles/Tester/BMRG/UK100/BMRG-M5-UK100-6M-P0_balanced_chart.set`  
SL 1800 / TP 2250 · ATR max 869 · magic 26101905 (ATR gate required).

**BMRG M15 tester preset:** `Profiles/Tester/BMRG/UK100/BMRG-M15-UK100-6M-P0_balanced_chart.set`  
SL 2500 / TP 3125 · ATR max 1470 · magic 26101201.

Models: `regimes.rule_v1` · `fit.map_v0` · `profiles.v1`  
Range: 2025-12-17 → 2026-10-11 · BMRG via `bmrg_uk100_m5_6m_audit.py` / `bmrg_uk100_m15_6m_audit.py`
