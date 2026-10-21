# TSLA research dossier

Living asset profile + 2-year monthly regime / fit audit produced from the local Ouroboros pipe.

| File | Contents |
| --- | --- |
| [`PROFILE.md`](./PROFILE.md) | Comprehensive asset profile (identity, clocks, character, path, narrative) |
| [`regime-audit.md`](./regime-audit.md) | Monthly H1/D1 regime shares + MATCH/MISMATCH/FRAGILE tags |
| [`profile.json`](./profile.json) | `profile.v1` snapshot |
| [`audit.json`](./audit.json) | Full machine export (boards, nowcast, news) |
| [`BMRG_M15_chart_preset.md`](./BMRG_M15_chart_preset.md) | BMRG M15 ~6m chart preset (Balanced 600/750 + ATR regime) |
| [`bmrg_m15_6m_audit.json`](./bmrg_m15_6m_audit.json) | BMRG M15 FIXED_RR probe scorecard |
| [`BMRG_M5_chart_preset.md`](./BMRG_M5_chart_preset.md) | BMRG M5 ~6m chart preset (Balanced 500/620 · session 15–19) |
| [`bmrg_m5_6m_audit.json`](./bmrg_m5_6m_audit.json) | BMRG M5 FIXED_RR probe scorecard |

**Canvas covers (open beside chat):**
- Asset profile: [tsla-asset-profile.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/tsla-asset-profile.canvas.tsx)
- BMRG M15: [bmrg-tsla-m15-preset.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/bmrg-tsla-m15-preset.canvas.tsx)
- BMRG M5: [bmrg-tsla-m5-preset.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/bmrg-tsla-m5-preset.canvas.tsx)

**MT5 presets:** `Experts/BMRG/Presets/BMRG-M15-TSLA-*` · `BMRG-M5-TSLA-*` · Tester `Profiles/Tester/BMRG/TSLA/`

Models: `regimes.rule_v1` · `fit.map_v0` · `profiles.v1`  
Range: 2024-10-07 → 2026-10-07 · scripts: `tsla_regime_audit.py` · `bmrg_tsla_m15_6m_audit.py` · `bmrg_tsla_m5_6m_audit.py`
