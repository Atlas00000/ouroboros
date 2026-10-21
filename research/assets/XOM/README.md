# XOM research dossier

Living asset profile + 2-year monthly regime / fit audit + BMRG M15 chart preset from the local Ouroboros pipe.

| File | Contents |
| --- | --- |
| [`PROFILE.md`](./PROFILE.md) | Comprehensive asset profile (identity, clocks, character, path, narrative) |
| [`regime-audit.md`](./regime-audit.md) | Monthly H1/D1 regime shares + MATCH/MISMATCH/FRAGILE tags |
| [`BMRG_M15_chart_preset.md`](./BMRG_M15_chart_preset.md) | BMRG M15 ~6m chart preset (TP>SL · ATR regime) |
| [`BMRG_M5_chart_preset.md`](./BMRG_M5_chart_preset.md) | BMRG M5 ~6m chart preset (TP>SL · ATR regime) |
| [`bmrg_m15_6m_audit.json`](./bmrg_m15_6m_audit.json) | M15* FIXED_RR probe ladder + meanrev months |
| [`bmrg_m5_6m_audit.json`](./bmrg_m5_6m_audit.json) | M5* FIXED_RR probe ladder + meanrev months |
| [`profile.json`](./profile.json) | `profile.v1` snapshot |
| [`audit.json`](./audit.json) | Full machine export (boards, nowcast, news) |

**Canvas covers (open beside chat):**
- [xom-asset-profile.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/xom-asset-profile.canvas.tsx)
- [bmrg-xom-m15-preset.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/bmrg-xom-m15-preset.canvas.tsx)
- [bmrg-xom-m5-preset.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/bmrg-xom-m5-preset.canvas.tsx)

**MT5 presets:** `Experts/BMRG/Presets/BMRG-M15-XOM-6M-P0_*.set` · `BMRG-M5-XOM-6M-P0_*.set` · Tester `Profiles/Tester/BMRG/XOM/`

Models: `regimes.rule_v1` · `fit.map_v0` · `profiles.v1`  
Range: 2024-10-07 → 2026-10-07 · BMRG window 2026-05 → 2026-10 · scripts `xom_regime_audit.py` / `bmrg_xom_m15_6m_audit.py` / `bmrg_xom_m5_6m_audit.py`
