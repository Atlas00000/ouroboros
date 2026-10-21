# MSFT research dossier

Living asset profile + 2-year monthly regime / fit audit + BMRG M15/M5 chart presets from the local Ouroboros pipe.

| File | Contents |
| --- | --- |
| [`PROFILE.md`](./PROFILE.md) | Comprehensive asset profile (identity, clocks, character, path, narrative) |
| [`regime-audit.md`](./regime-audit.md) | Monthly H1/D1 regime shares + MATCH/MISMATCH/FRAGILE tags |
| [`BMRG_M15_chart_preset.md`](./BMRG_M15_chart_preset.md) | BMRG M15 ~6m chart preset (TP≥SL · regime-filtered) |
| [`BMRG_M5_chart_preset.md`](./BMRG_M5_chart_preset.md) | BMRG M5 ~6m chart preset (TP≥SL · regime-filtered) |
| [`bmrg_m15_6m_audit.json`](./bmrg_m15_6m_audit.json) | BMRG M15* FIXED_RR probe scorecard |
| [`bmrg_m5_6m_audit.json`](./bmrg_m5_6m_audit.json) | BMRG M5* FIXED_RR probe scorecard |
| [`profile.json`](./profile.json) | `profile.v1` snapshot |
| [`audit.json`](./audit.json) | Full machine export (boards, nowcast, news) |

**Canvas covers (open beside chat):**
- [msft-asset-profile.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/msft-asset-profile.canvas.tsx)
- [bmrg-msft-m15-preset.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/bmrg-msft-m15-preset.canvas.tsx)
- [bmrg-msft-m5-preset.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/bmrg-msft-m5-preset.canvas.tsx)

**MT5 Tester folder:** `MQL5/Profiles/Tester/BMRG/MSFT/`  
- M15: `BMRG-M15-MSFT-6M-P0_*.set` · magics 26101901 / 26101902  
- M5: `BMRG-M5-MSFT-6M-P0_balanced_TPgtSL.set` · magic **26101903**

Models: `regimes.rule_v1` · `fit.map_v0` · `profiles.v1`  
Profile range: 2024-10-07 → 2026-10-07 · BMRG window: 2026-05-01 → 2026-10-07  
Scripts: `msft_regime_audit.py` · `bmrg_msft_m15_6m_audit.py` · `bmrg_msft_m5_6m_audit.py`
