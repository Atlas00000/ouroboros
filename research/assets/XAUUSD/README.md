# XAUUSD research dossier

Living asset profile + 2-year monthly regime / fit audit + BMRG M15 chart preset from the local Ouroboros pipe.

| File | Contents |
| --- | --- |
| [`PROFILE.md`](./PROFILE.md) | Comprehensive asset profile (identity, clocks, character, path, narrative) |
| [`regime-audit.md`](./regime-audit.md) | Monthly H1/D1 regime shares + MATCH/MISMATCH/FRAGILE tags |
| [`profile.json`](./profile.json) | `profile.v1` snapshot |
| [`audit.json`](./audit.json) | Full machine export (boards, nowcast, news) |
| [`BMRG_M15_chart_preset.md`](./BMRG_M15_chart_preset.md) | BMRG M15 ~6m balanced geometry + ATR regime gate |
| [`bmrg_m15_6m_audit.json`](./bmrg_m15_6m_audit.json) | Machine audit (probes, monthly meanrev, ATR stats) |
| [`BMRG_M5_chart_preset.md`](./BMRG_M5_chart_preset.md) | BMRG **M5** ~6m balanced geometry + ATR regime gate |
| [`bmrg_m5_6m_audit.json`](./bmrg_m5_6m_audit.json) | M5 probe audit |

**Canvas covers (open beside chat):**
- Profile: [xauusd-asset-profile.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/xauusd-asset-profile.canvas.tsx)
- BMRG M15: [bmrg-xauusd-m15-preset.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/bmrg-xauusd-m15-preset.canvas.tsx)

**BMRG Tester dir:** `…/MQL5/Profiles/Tester/BMRG/XAUUSD/`  

### M5 (new)

| Preset | Magic | Notes |
| --- | ---: | --- |
| **M5 P0 balanced** | **26101950** | SL **680** / TP **850** · RR **1.25** · ATR≤**575** · probe WR≈45.9% · E_N≈+0.03R |

### M15 ladder

| Preset | Magic | Notes |
| --- | ---: | --- |
| P0 balanced | 26100915 | FAILED every-tick (WR≈43% &lt; BWR) · RR 1.25 |
| P1 selective | 26100916 | BBDev **2.4** · CD **3** · BBw min **0.35%** · FAIL same WR |
| P2 fadeConfirm | 26100917 | FAILED WR≈20% · equity halt |
| P3 lower-BWR | 26100918 | RR **1.35** (1200/1620) · mixed; hi-vol/continuation DD |
| P4 wrFocus | 26100919 | RR **1.0** (1200/1200) · BWR **50%** · ATR≤**800** |

Hard rule: never TP &lt; SL · session 12–20 · skip Tue · fade OFF  

Models: `regimes.rule_v1` · `fit.map_v0` · `profiles.v1`  
Scripts: `xauusd_regime_audit.py` · `bmrg_xauusd_m15_6m_audit.py` · `bmrg_xauusd_m5_6m_audit.py`
