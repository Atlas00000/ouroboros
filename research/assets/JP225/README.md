# JP225 research dossier

Living asset profile + monthly regime / fit audit + BMRG M15/M5 chart presets from the local Ouroboros pipe.

> **Depth:** YWO MT5 `JP225`/`JPN225` history starts 2024-10-07 (≈730d M1). Requested 2y; boards cover available broker depth.

| File | Contents |
| --- | --- |
| [`PROFILE.md`](./PROFILE.md) | Comprehensive asset profile (identity, clocks, character, path, narrative) |
| [`regime-audit.md`](./regime-audit.md) | Monthly H1/D1 regime shares + MATCH/MISMATCH/FRAGILE tags |
| [`BMRG_M15_chart_preset.md`](./BMRG_M15_chart_preset.md) | BMRG M15 ~6m growth + ATR-regime chart preset (TP&gt;SL) |
| [`BMRG_M5_chart_preset.md`](./BMRG_M5_chart_preset.md) | BMRG M5 ~6m growth RR2 + ATR-band chart preset (TP&gt;SL) |
| [`bmrg_m15_6m_audit.json`](./bmrg_m15_6m_audit.json) | M15* geometry probe + monthly meanrev boards |
| [`bmrg_m5_6m_audit.json`](./bmrg_m5_6m_audit.json) | M5* lean geometry probe (viable_count=0 under RR≤1.5) |
| [`bmrg_m5_wr_lift.json`](./bmrg_m5_wr_lift.json) | M5 WR-lift — sole Stage-1 pass (RR=2.0 + ATR band) |
| [`profile.json`](./profile.json) | `profile.v1` snapshot |
| [`audit.json`](./audit.json) | Full machine export (boards, nowcast, news) |

**Canvas covers (open beside chat):**
- Profile: [jp225-asset-profile.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/jp225-asset-profile.canvas.tsx)
- BMRG M15: [bmrg-jp225-m15-preset.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/bmrg-jp225-m15-preset.canvas.tsx)
- BMRG M5: [bmrg-jp225-m5-preset.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/bmrg-jp225-m5-preset.canvas.tsx)

**MT5 load — M5 P0 (NEW):** `Experts\BMRG\Presets\BMRG-M5-JP225-6M-P0_growth_chart.set` · magic **26101906** · SL/TP **25000/50000** (RR=2.0) · BB 2.5 · ATR∈[7610,11285] · CD 3 · deposit unchanged  

**MT5 load — M15 (NEXT = P1.5 light):** `Experts\BMRG\Presets\BMRG-M15-JP225-6M-P1p5_light_chart.set` · magic **26101905** · BB 2.3 · CD 4 · ATR≤18620 · Fade OFF · SL/TP frozen · deposit unchanged  

Tester `Profiles/Tester/BMRG/JP225/` · symbol **JPN225**

**Blotters (M15):** P0 (26101903) tip WR 42.4% · EF −1.1pp · P1 fade (26101904) tip WR **43.0%** · EF **−0.8pp** (still Stage 1 fail). Scores: [`tester_magic_26101903_score.json`](./tester_magic_26101903_score.json) · [`tester_magic_26101904_score.json`](./tester_magic_26101904_score.json)

Models: `regimes.rule_v1` · `fit.map_v0` · `profiles.v1`  
Scripts: `jp225_regime_audit.py` · `bmrg_jp225_m15_6m_audit.py` · `bmrg_jp225_m15_p1_wr_lift.py` · `bmrg_jp225_m5_6m_audit.py` · `bmrg_jp225_m5_wr_lift.py` · `_score_magic_26101903.py`
