# US30 research dossier

Living asset profile + monthly regime / fit audit + BMRG M15/M5 chart presets from the local Ouroboros pipe.

> **Depth:** YWO MT5 `US30` history 2024-09-12 → 2026-10-07 (≈755d M1 ≈ 2.1y). Full requested 2y monthly board.

| File | Contents |
| --- | --- |
| [`PROFILE.md`](./PROFILE.md) | Comprehensive asset profile (identity, clocks, character, path, narrative) |
| [`regime-audit.md`](./regime-audit.md) | Monthly H1/D1 regime shares + MATCH/MISMATCH/FRAGILE tags |
| [`profile.json`](./profile.json) | `profile.v1` snapshot |
| [`audit.json`](./audit.json) | Full machine export (boards, nowcast, news) |
| [`bmrg_m15_6m_audit.json`](./bmrg_m15_6m_audit.json) | BMRG M15* ~6m geometry probe (framework Stage 0–1) |
| [`BMRG_M15_chart_preset.md`](./BMRG_M15_chart_preset.md) | BMRG M15 chart/tester preset card |
| [`bmrg_m5_6m_audit.json`](./bmrg_m5_6m_audit.json) | BMRG M5* ~6m geometry probe (framework Stage 0–1) |
| [`BMRG_M5_chart_preset.md`](./BMRG_M5_chart_preset.md) | BMRG M5 chart/tester preset card |

**Canvas covers (open beside chat):**
- [us30-asset-profile.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/us30-asset-profile.canvas.tsx) — 2y regime dossier
- [bmrg-us30-m15-preset.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/bmrg-us30-m15-preset.canvas.tsx) — BMRG M15 geometry
- [bmrg-us30-m5-preset.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/bmrg-us30-m5-preset.canvas.tsx) — BMRG M5 geometry

**BMRG tester presets** (`Profiles/Tester/BMRG/US30/`, also under `Experts/BMRG/Presets/`):

| TF | Preset | SL / TP | ATR max | Magic |
| --- | --- | --- | ---: | ---: |
| M15 | `BMRG-M15-US30-6M-P0_balanced_chart.set` | 4150 / 5190 | 8100 | 26101903 |
| M5 | `BMRG-M5-US30-6M-P0_balanced_chart.set` | 3620 / 4520 | 3550 | 26101904 |

Models: `regimes.rule_v1` · `fit.map_v0` · `profiles.v1`  
Range: 2024-09-12 → 2026-10-07 · regenerated via `us30_regime_audit.py` · BMRG via `bmrg_us30_m15_6m_audit.py` / `bmrg_us30_m5_6m_audit.py`
