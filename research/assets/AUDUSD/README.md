# AUDUSD research dossier

Living asset profile + 2-year monthly regime / fit audit + BMRG M15 chart preset from the local Ouroboros pipe.

| File | Contents |
| --- | --- |
| [`PROFILE.md`](./PROFILE.md) | Comprehensive asset profile (identity, clocks, character, path, narrative) |
| [`regime-audit.md`](./regime-audit.md) | Monthly H1/D1 regime shares + MATCH/MISMATCH/FRAGILE tags |
| [`BMRG_M15_chart_preset.md`](./BMRG_M15_chart_preset.md) | BMRG M15 ~6m balanced geometry + ATR regime chart card |
| [`bmrg_m15_6m_audit.json`](./bmrg_m15_6m_audit.json) | M15* FIXED_RR probe export (Stage 0–1 design prior) |
| [`profile.json`](./profile.json) | `profile.v1` snapshot |
| [`audit.json`](./audit.json) | Full machine export (boards, nowcast, news) |

**Canvas covers (open beside chat):**
- [audusd-asset-profile.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/audusd-asset-profile.canvas.tsx) — 2y dossier
- [bmrg-audusd-m15-preset.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/bmrg-audusd-m15-preset.canvas.tsx) — BMRG M15 P0

**MT5 preset:** `Experts/BMRG/Presets/BMRG-M15-AUDUSD-6M-P0_balanced_chart.set` · magic **26101901** · SL/TP **130/170** · ATR max **55**

Models: `regimes.rule_v1` · `fit.map_v0` · `profiles.v1`  
Profile range: 2024-09-12 → 2026-09-21 · BMRG tip: 2026-04-01 → 2026-09-21  
Regenerate: `server/scripts/audusd_regime_audit.py` · `server/scripts/bmrg_audusd_m15_6m_audit.py`
