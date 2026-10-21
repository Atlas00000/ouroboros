# DE40 research dossier

Living asset profile + monthly regime / fit audit produced from the local Ouroboros pipe.

> **Depth:** YWO MT5 `DE40`/`DE30` history starts 2025-06-05 (≈489d M1). Requested 2y; boards cover available broker depth.

| File | Contents |
| --- | --- |
| [`PROFILE.md`](./PROFILE.md) | Comprehensive asset profile (identity, clocks, character, path, narrative) |
| [`regime-audit.md`](./regime-audit.md) | Monthly H1/D1 regime shares + MATCH/MISMATCH/FRAGILE tags |
| [`BMRG_M15_chart_preset.md`](./BMRG_M15_chart_preset.md) | BMRG M15 ~6m balanced chart preset (TP&gt;SL · ATR regime) |
| [`BMRG_M5_chart_preset.md`](./BMRG_M5_chart_preset.md) | BMRG M5 ~6m balanced chart preset (TP&gt;SL · ATR regime) |
| [`bmrg_m15_6m_audit.json`](./bmrg_m15_6m_audit.json) | M15* FIXED_RR geometry probe + monthly meanrev tags |
| [`bmrg_m5_6m_audit.json`](./bmrg_m5_6m_audit.json) | M5* FIXED_RR geometry probe + monthly meanrev tags |
| [`profile.json`](./profile.json) | `profile.v1` snapshot |
| [`audit.json`](./audit.json) | Full machine export (boards, nowcast, news) |

**Canvas covers (open beside chat):**
- Profile: [de40-asset-profile.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/de40-asset-profile.canvas.tsx)
- BMRG M15: [bmrg-de40-m15-preset.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/bmrg-de40-m15-preset.canvas.tsx)
- BMRG M5: [bmrg-de40-m5-preset.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/bmrg-de40-m5-preset.canvas.tsx)

**MT5:**
- M15 → `Presets/BMRG-M15-DE40-6M-P0_balanced_chart.set` (magic **26101902**)
- M5 → `Presets/BMRG-M5-DE40-6M-P0_balanced_chart.set` (magic **26101903**)
- Tester: `MQL5/Profiles/Tester/BMRG/DE40/`

Models: `regimes.rule_v1` · `fit.map_v0` · `profiles.v1`  
Range: 2025-06-05 → 2026-10-07 · scripts: `de40_regime_audit.py` / `bmrg_de40_m15_6m_audit.py` / `bmrg_de40_m5_6m_audit.py`
