# EURGBP research dossier

Living asset profile + 2-year monthly regime / fit audit + BMRG M15/M5 chart presets from the local Ouroboros pipe.

| File | Contents |
| --- | --- |
| [`PROFILE.md`](./PROFILE.md) | Comprehensive asset profile (identity, clocks, character, path, narrative) |
| [`regime-audit.md`](./regime-audit.md) | Monthly H1/D1 regime shares + MATCH/MISMATCH/FRAGILE tags |
| [`profile.json`](./profile.json) | `profile.v1` snapshot |
| [`audit.json`](./audit.json) | Full machine export (boards, nowcast, news) |
| [`BMRG_M15_chart_preset.md`](./BMRG_M15_chart_preset.md) | BMRG M15 ~6m balanced geometry + ATR regime gate |
| [`bmrg_m15_6m_audit.json`](./bmrg_m15_6m_audit.json) | M15 machine audit |
| [`BMRG_M5_chart_preset.md`](./BMRG_M5_chart_preset.md) | BMRG M5 ~6m balanced geometry + ATR regime gate |
| [`bmrg_m5_6m_audit.json`](./bmrg_m5_6m_audit.json) | M5 machine audit |

**Canvas covers (open beside chat):**
- Profile: [eurgbp-asset-profile.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/eurgbp-asset-profile.canvas.tsx)
- BMRG M15: [bmrg-eurgbp-m15-preset.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/bmrg-eurgbp-m15-preset.canvas.tsx)
- BMRG M5: [bmrg-eurgbp-m5-preset.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/bmrg-eurgbp-m5-preset.canvas.tsx)

**BMRG Tester dir:** `…/MQL5/Profiles/Tester/BMRG/EURGBP/`  
| Preset | Magic | Notes |
| --- | ---: | --- |
| M15 P0 balanced | 26101215 | SL **50** / TP **65** · RR **1.30** · ATR≤**28** |
| **M5 P0 balanced** | **26101950** | SL **50** / TP **65** · RR **1.30** · ATR≤**18** · CD 3 |

Hard rule: never TP &lt; SL · MaxSpread 18 · AOS OFF · session 12–20 · skip Tue  
Models: `regimes.rule_v1` · `fit.map_v0` · `profiles.v1`  
Profile range: 2024-09-12 → 2026-09-11 · BMRG window: 2026-04-01 → 2026-09-11  
Scripts: `eurgbp_regime_audit.py` · `bmrg_eurgbp_m15_6m_audit.py` · `bmrg_eurgbp_m5_6m_audit.py`
