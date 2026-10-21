# XBRUSD research dossier

Living asset profile + 2-year monthly regime / fit audit + BMRG M15/M5 chart presets from the local Ouroboros pipe.

| File | Contents |
| --- | --- |
| [`PROFILE.md`](./PROFILE.md) | Comprehensive asset profile (identity, clocks, character, path, narrative) |
| [`regime-audit.md`](./regime-audit.md) | Monthly H1/D1 regime shares + MATCH/MISMATCH/FRAGILE tags |
| [`profile.json`](./profile.json) | `profile.v1` snapshot |
| [`audit.json`](./audit.json) | Full machine export (boards, nowcast, news) |
| [`BMRG_M15_chart_preset.md`](./BMRG_M15_chart_preset.md) | BMRG M15 ~6m pointer |
| [`bmrg_m15_6m_audit.json`](./bmrg_m15_6m_audit.json) | M15 machine audit |
| [`BMRG_M5_chart_preset.md`](./BMRG_M5_chart_preset.md) | BMRG M5 ~6m buy-only balanced + ATR |
| [`bmrg_m5_6m_audit.json`](./bmrg_m5_6m_audit.json) | M5 both-sides probe grid |
| [`bmrg_m5_buyonly_ablation.json`](./bmrg_m5_buyonly_ablation.json) | M5 side / BB / ATR ablation |

**Canvas covers (open beside chat):**
- Profile: [xbrusd-asset-profile.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/xbrusd-asset-profile.canvas.tsx)
- BMRG M15: [bmrg-xbrusd-m15-preset.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/bmrg-xbrusd-m15-preset.canvas.tsx)
- BMRG M5: [bmrg-xbrusd-m5-preset.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/bmrg-xbrusd-m5-preset.canvas.tsx)

**BMRG Tester dir:** `…/MQL5/Profiles/Tester/BMRG/XBRUSD/`  

| TF | Preset | Magic | Notes |
| --- | --- | ---: | --- |
| **M5** | **P0 buyOnly balanced** | **26101950** | SL **390**/TP **490** · BB **2.5** · ATR≤**315** · sell OFF |
| M15 | P0 balanced | 26101220 | ATR≤70 (wrong scale) → ZERO TRADES |
| M15 | P0b atrNative | 26101221 | ATR≤525 · both · FAIL (sells drag) |
| M15 | P1 buyOnly | 26101222 | P0b geom · sell OFF |

Hard rule: never TP &lt; SL · G0 MaxLevels=1 · AOS OFF · EA Point Digits=3  
Framework: `docs/framework/unified_edge_framework.md`

Models: `regimes.rule_v1` · `fit.map_v0` · `profiles.v1`  
BMRG window: 2026-05-01 → 2026-10-07  
Scripts: `xbrusd_regime_audit.py` · `bmrg_xbrusd_m15_6m_audit.py` · `bmrg_xbrusd_m5_6m_audit.py`
