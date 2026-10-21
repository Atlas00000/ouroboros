# USDCAD research dossier

Living asset profile + 2-year monthly regime / fit audit + BMRG M15/M5 chart presets from the local Ouroboros pipe.

| File | Contents |
| --- | --- |
| [`PROFILE.md`](./PROFILE.md) | Comprehensive asset profile (identity, clocks, character, path, narrative) |
| [`regime-audit.md`](./regime-audit.md) | Monthly H1/D1 regime shares + MATCH/MISMATCH/FRAGILE tags |
| [`BMRG_M15_chart_preset.md`](./BMRG_M15_chart_preset.md) | BMRG M15 ~6m chart preset card |
| [`BMRG_M5_chart_preset.md`](./BMRG_M5_chart_preset.md) | BMRG M5 ~6m chart preset card |
| [`profile.json`](./profile.json) | `profile.v1` snapshot |
| [`audit.json`](./audit.json) | Full machine export (boards, nowcast, news) |
| [`bmrg_m15_6m_audit.json`](./bmrg_m15_6m_audit.json) | M15* FIXED_RR probe grid |
| [`bmrg_m5_6m_audit.json`](./bmrg_m5_6m_audit.json) | M5* FIXED_RR probe grid |

**Canvas covers** (open beside chat):

- Asset profile: [usdcad-asset-profile.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/usdcad-asset-profile.canvas.tsx)
- BMRG M15: [bmrg-usdcad-m15-preset.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/bmrg-usdcad-m15-preset.canvas.tsx)
- BMRG M5: [bmrg-usdcad-m5-preset.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/bmrg-usdcad-m5-preset.canvas.tsx)

**MT5 load**

| TF | Preset | Magic |
| --- | --- | ---: |
| M15 | `Experts/BMRG/Presets/BMRG-M15-USDCAD-6M-P0_selective_chart.set` | **26101901** |
| M5 | `Experts/BMRG/Presets/BMRG-M5-USDCAD-6M-P0_balanced_chart.set` | **26101905** |

Tester: `Profiles/Tester/BMRG/USDCAD/`

Models: `regimes.rule_v1` · `fit.map_v0` · `profiles.v1`  
Profile range: 2024-09-12 → 2026-09-21 · BMRG window: 2026-04-01 → 2026-09-21  
Scripts: `usdcad_regime_audit.py` · `bmrg_usdcad_m15_6m_audit.py` · `bmrg_usdcad_m5_6m_audit.py`
