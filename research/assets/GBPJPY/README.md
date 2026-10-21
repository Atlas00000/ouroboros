# GBPJPY research dossier

Living asset profile + 2-year monthly regime / fit audit + BMRG M15 / M5 chart presets from the local Ouroboros pipe.

| File | Contents |
| --- | --- |
| [`PROFILE.md`](./PROFILE.md) | Comprehensive asset profile |
| [`regime-audit.md`](./regime-audit.md) | Monthly H1/D1 regime + fit tags |
| [`profile.json`](./profile.json) | `profile.v1` snapshot |
| [`audit.json`](./audit.json) | Full machine export |
| [`BMRG_M15_chart_preset.md`](./BMRG_M15_chart_preset.md) | BMRG M15 P0 → P1 → **P1.5** ladder |
| [`bmrg_m15_6m_audit.json`](./bmrg_m15_6m_audit.json) | M15 P0 geometry / ATR audit |
| [`bmrg_m15_p1_wr_lift.json`](./bmrg_m15_p1_wr_lift.json) | M15 P1 WR-lift probe + Leak rescore |
| [`BMRG_M5_chart_preset.md`](./BMRG_M5_chart_preset.md) | BMRG **M5** P0 balanced (ATR-scaled) |
| [`bmrg_m5_6m_audit.json`](./bmrg_m5_6m_audit.json) | M5 lean geometry / regime audit |

**Canvas (M5):** [bmrg-gbpjpy-m5-preset.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/bmrg-gbpjpy-m5-preset.canvas.tsx)  
**Canvas (M15):** [bmrg-gbpjpy-m15-preset.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/bmrg-gbpjpy-m15-preset.canvas.tsx)

**BMRG Tester:** `…/MQL5/Profiles/Tester/BMRG/GBPJPY/`

### M5 sleeve (chart TF M5)

| Preset | Magic | Status |
| --- | ---: | --- |
| **P0 balanced 140/180** | **26101835** | **NEXT** · BB 2.2 · CD 3 · MaxSpr 40 · ATR OFF · session 12–20 |

Tester dates: **2026.04.01 → 2026.09.11**. Probe: n=378 · WR 45.8% &gt; BWR 43.7% · E_N +0.046R · EF thin under 58pt prior.

### M15 sleeve (chart TF M15)

| Preset | Magic | Status |
| --- | ---: | --- |
| P0 balanced | 26101825 | FAILED WR 41% &lt; BWR |
| P1 WR-lift | 26101826 | FAILED starved (n=4) |
| **P1.5 light** | **26101827** | **NEXT** · BB 2.3 · CD 3 · Fade OFF · MaxSpr 32 · SL/TP 160/200 |

Tester dates for P1.5: **2026.05.01 → 2026.09.11** only.  
Hard rule: never TP &lt; SL · do not widen TP / shrink SL to fix WR.