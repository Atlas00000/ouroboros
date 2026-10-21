"""Render research/assets/MSFT markdown from audit.json."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


def pct(x: float | None, digits: int = 1) -> str:
    if x is None:
        return "—"
    return f"{100 * float(x):.{digits}f}%"


def fnum(x: object | None, digits: int = 2) -> str:
    if x is None:
        return "—"
    return f"{float(x):.{digits}f}"


def _fit_interp(fit30: dict) -> str:
    mr = fit30["meanrev"]
    tf = fit30["trendfollow"]
    mr_s = mr["shares"]
    lead = "ranging" if mr_s["MATCH"] >= mr_s["MISMATCH"] else "trend"
    return (
        f"Interpretation: last ~30d H1 mass is **{lead}-contested** — "
        f"meanrev={mr['tag']} ({pct(mr_s['MATCH'])} MATCH / "
        f"{pct(mr_s['MISMATCH'])} MISMATCH), trendfollow={tf['tag']} "
        f"({pct(tf['shares']['MATCH'])} MATCH). FRAGILE sleeve "
        f"{pct(mr_s['FRAGILE'])}."
    )


def _regime_read(rd: list[dict]) -> str:
    by = {r["regime"]: float(r["share"]) for r in rd}
    ranging = by.get("ranging", 0)
    hv = by.get("high_volatility", 0)
    up = by.get("trending_up", 0)
    down = by.get("trending_down", 0)
    net_trend = up + down
    lean = "meanrev-leaning" if ranging >= net_trend else "trend-leaning"
    return (
        f"**Read:** ranging ({pct(ranging)}) + high_volatility ({pct(hv)}) "
        f"vs net trending ({pct(net_trend)}). On this sample MSFT is "
        f"**{lean}** on H1 history — with a material fragile/high-vol sleeve."
    )


def _corr_read(corrs: list[dict]) -> str:
    ranked = sorted(corrs, key=lambda c: abs(float(c["coefficient"])), reverse=True)
    top = ranked[:4]
    neg = [c for c in ranked if float(c["coefficient"]) < -0.05][:2]
    bits = [
        f"{c['symbol']} ({float(c['coefficient']):+.2f})" for c in top
    ]
    line = "Closest sleeves this window: " + ", ".join(bits) + "."
    if neg:
        line += " Notable negative: " + ", ".join(
            f"{c['symbol']} ({float(c['coefficient']):+.2f})" for c in neg
        ) + "."
    return line


def _fragile_clusters(h1_rows: list[dict]) -> list[str]:
    out: list[str] = []
    for r in h1_rows:
        if r.get("meanrev_tag") == "FRAGILE" or r.get("trendfollow_tag") == "FRAGILE":
            out.append(r["month"])
    return out


def _trend_match_months(h1_rows: list[dict]) -> list[str]:
    return [r["month"] for r in h1_rows if r.get("trendfollow_tag") == "MATCH"]


def main() -> int:
    repo = Path(__file__).resolve().parents[2]
    out = repo / "research" / "assets" / "MSFT"
    d = json.loads((out / "audit.json").read_text(encoding="utf-8"))
    prof = d["profile"]
    nc = d["nowcast"]
    dr = d["data_range"]
    id_ = prof["identity"]
    vol = prof["volatility"]
    liq = prof["liquidity"]
    hours = prof["trading_hours"]
    rd = prof["regime_distribution"]
    fit30 = nc["fit_30d_h1"]
    st = nc["state"]
    sent = nc["sentiment"]
    ins = nc.get("insight") or {}
    px = d["monthly_price"]
    tot_ret = (px[-1]["close"] / px[0]["open"] - 1) * 100 if px else None
    h1_rows = d["monthly_regime_table_h1"]
    d1_rows = d["monthly_regime_table_d1"]
    dom_h1 = Counter(r["dominant_regime"] for r in h1_rows)
    dom_d1 = Counter(r["dominant_regime"] for r in d1_rows)
    tsum = d["tag_summary"]
    n_h1 = len(h1_rows)
    mr_match = tsum.get("H1|meanrev", {}).get("MATCH", 0)
    tf_match = tsum.get("H1|trendfollow", {}).get("MATCH", 0)
    fragile = _fragile_clusters(h1_rows)
    trend_months = _trend_match_months(h1_rows)
    modal = dom_h1.most_common(1)[0] if dom_h1 else ("?", 0)

    lines: list[str] = []
    A = lines.append
    A("# MSFT — Asset profile dossier")
    A("")
    A(
        "> Research / advisory only · Ouroboros `profile.v1` + `regimes.rule_v1` + `fit.map_v0`  "
    )
    A(
        f"> Generated `{d['generated_at'][:19]}Z` · data `{dr['d1_start'][:10]}` → "
        f"`{dr['d1_end'][:10]}` ({dr['month_count']} calendar months, "
        f"M1 depth ≈ {dr['m1_depth_days']:.0f}d)"
    )
    A("")
    A(
        "Canvas cover (open beside chat): "
        "[`msft-asset-profile.canvas.tsx`](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/msft-asset-profile.canvas.tsx)."
    )
    A("")
    A("---")
    A("")
    A("## Identity")
    A("")
    A("| Field | Value |")
    A("| --- | --- |")
    A(f"| Symbol | `{id_['symbol']}` |")
    A(f"| Display | {id_['display_name']} |")
    A(f"| Class | {id_['asset_class']} |")
    A(f"| Quote | {id_['quote_currency']} |")
    A(f"| MT5 ticker | `{id_['mt5_ticker']}` |")
    A(
        f"| Sessions | {', '.join(hours['sessions'])} · `{hours['timezone']}` · "
        f"UTC {hours['open_utc'][:5]}–{hours['close_utc'][:5]} |"
    )
    A("")
    A(hours["notes"])
    A("")
    A("---")
    A("")
    A("## Two clocks")
    A("")
    A("### Nowcast (H1 state)")
    A("")
    if st:
        A("| Metric | Value |")
        A("| --- | --- |")
        A(f"| Confirmed regime | **{st['regime']}** |")
        A(f"| Vol percentile | {fnum(st['volatility_percentile'], 1)} |")
        A(f"| Trend ER | {fnum(st['trend_strength'], 3)} |")
        A(f"| Confidence | {fnum(st['confidence'], 3)} |")
        A(f"| As-of | {st['as_of']} |")
        A(f"| Stale | {st['stale']} |")
        A("")
        probs = json.loads(st["probabilities_json"])
        A(
            "Soft probabilities (nowcast — may disagree with confirmed label when "
            "confidence is low):"
        )
        A("")
        A("| Regime | P |")
        A("| --- | ---: |")
        for p in probs:
            A(f"| {p['regime']} | {pct(p['probability'])} |")
        A("")
    else:
        A("_No H1 state row — run `regime_log`._")
        A("")

    A("### Live fit gate (ex-post 30d H1 shares → dominant tag)")
    A("")
    A("| Family | Tag | MATCH | MISMATCH | FRAGILE | Bars |")
    A("| --- | --- | ---: | ---: | ---: | ---: |")
    for fam in ("meanrev", "trendfollow"):
        b = fit30[fam]
        s = b["shares"]
        A(
            f"| `{fam}` | **{b['tag']}** | {pct(s['MATCH'])} | "
            f"{pct(s['MISMATCH'])} | {pct(s['FRAGILE'])} | {b['bar_count']} |"
        )
    A("")
    A(_fit_interp(fit30))
    A("")
    A("---")
    A("")
    A("## Character (`profile.v1`)")
    A("")
    A("### Volatility & liquidity")
    A("")
    A("| Field | Value |")
    A("| --- | --- |")
    A(f"| ATR pctile 30d | {fnum(vol['atr_percentile_30d'], 1)} |")
    A(f"| Realized vol pctile 30d | {fnum(vol['realized_vol_percentile_30d'], 1)} |")
    A(f"| Typical daily range | {fnum(vol['typical_daily_range'], 2)} USD |")
    A(f"| Range pctile 30d (liq proxy) | {fnum(liq['spread_percentile_30d'], 1)} |")
    A("| True spread | deferred |")
    A("")
    A(f"_{liq['notes']}_")
    A("")
    A("### Regime distribution (history clock)")
    A("")
    A(
        "Confirmed-label share over the profile sample "
        "(H1 preferred when depth gate passes):"
    )
    A("")
    A("| Regime | Share |")
    A("| --- | ---: |")
    for r in rd:
        A(f"| {r['regime']} | {pct(r['share'])} |")
    A("")
    A(_regime_read(rd))
    A("")
    A("### Peer correlations (H1 ~30d)")
    A("")
    A("| Peer | ρ |")
    A("| --- | ---: |")
    for c in prof["correlations"]:
        A(f"| {c['symbol']} | {c['coefficient']:+.3f} |")
    A("")
    A(_corr_read(prof["correlations"]))
    A("")
    A("### Event sensitivities")
    A("")
    A(
        "Taxonomy present (NFP / CPI / FOMC) but **ATR multiples empty** — "
        "calendar hits scored for MSFT are below the ≥3-window gate. Honest gap "
        "until equity event windows are scored."
    )
    A("")
    A("---")
    A("")
    A("## Path")
    A("")
    if tot_ret is not None:
        A(
            f"Monthly D1 path return over the window: **{tot_ret:+.1f}%** "
            f"(open {px[0]['open']:.2f} → last close {px[-1]['close']:.2f})."
        )
    A("")
    A("| Month | Ret % | Close |")
    A("| --- | ---: | ---: |")
    for r in px:
        A(f"| {r['month']} | {r['ret_pct']:+.2f} | {r['close']:.2f} |")
    A("")
    A("---")
    A("")
    A("## Narrative pressure")
    A("")
    if sent:
        A(
            f"- Sentiment score: **{fnum(sent['score'], 3)}** on [−1, +1] · "
            f"{sent['item_count']} items · {sent['window_hours']}h window"
        )
        A(f"- As-of: {sent['as_of']} · stale={sent['stale']}")
    A(f"- Mapped news articles: **{d['news_count']}**")
    if ins:
        body = str(ins.get("body") or "")[:280]
        A(f"- Insight: _{ins.get('title')}_ — {body}")
    A("")
    A("Recent headlines:")
    A("")
    for n in d["recent_news"][:8]:
        A(
            f"- {str(n.get('published_at') or '')[:10]} · "
            f"{n.get('source') or '?'} — {n.get('headline')}"
        )
    A("")
    A("---")
    A("")
    A("## Provenance")
    A("")
    A(
        f"- Models: `{d['models']['regime']}` · `{d['models']['fit']}` · "
        f"`{d['models']['profile']}`"
    )
    A(
        f"- Profile confidence: {prof['provenance']['confidence']} · "
        f"stale={prof['provenance']['stale']}"
    )
    A(f"- Sources: {', '.join(prof['provenance']['sources'])}")
    A(
        "- Raw export: [`audit.json`](./audit.json) · monthly boards: "
        "[`regime-audit.md`](./regime-audit.md)"
    )
    A("")
    A(d["disclaimer"])
    A("")
    (out / "PROFILE.md").write_text("\n".join(lines), encoding="utf-8")

    L: list[str] = []
    B = L.append
    B("# MSFT — Regime audit & fit tagging (monthly, 2y)")
    B("")
    B(
        f"> Ex-post calendar-month boards · `{d['models']['regime']}` labels → "
        f"`{d['models']['fit']}`  "
    )
    B(
        f"> Window: {dr['months'][0]} → {dr['months'][-1]} "
        f"({n_h1} H1 months with confirmed bars after warmup)"
    )
    B("")
    B("## Method")
    B("")
    B("1. Load H1 / D1 OHLCV (~800d lookback; M1 depth gate passes).")
    B("2. Run `regime_feature_frame` → confirmed regime per bar.")
    B(
        "3. Slice each calendar month; map regimes → MATCH / MISMATCH / FRAGILE "
        "per edge family."
    )
    B(
        "4. Dominant tag = largest fit-share "
        "(ties break MISMATCH > FRAGILE > MATCH)."
    )
    B("")
    B(
        "Families: **meanrev** home=`ranging`; **trendfollow** "
        "home=`trending_up|trending_down`; both treat `high_volatility` as FRAGILE."
    )
    B("")
    B("## Tag summary (months with bars)")
    B("")
    B("| TF × family | MATCH | MISMATCH | FRAGILE |")
    B("| --- | ---: | ---: | ---: |")
    for key in (
        "H1|meanrev",
        "H1|trendfollow",
        "D1|meanrev",
        "D1|trendfollow",
    ):
        s = tsum.get(key, {})
        B(
            f"| `{key}` | {s.get('MATCH', 0)} | {s.get('MISMATCH', 0)} | "
            f"{s.get('FRAGILE', 0)} |"
        )
    B("")
    B(f"Dominant-regime months (H1): {dict(dom_h1)}")
    B(f"Dominant-regime months (D1): {dict(dom_d1)}")
    B("")
    B("## H1 monthly board")
    B("")
    B(
        "| Month | Dominant regime | meanrev | trendfollow | Bars | "
        "ranging | trend↑ | trend↓ | high_vol |"
    )
    B("| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |")
    for r in h1_rows:
        rs = r["regime_shares"]
        B(
            f"| {r['month']} | {r['dominant_regime']} | "
            f"**{r.get('meanrev_tag')}** | **{r.get('trendfollow_tag')}** | "
            f"{r['bar_count']} | {pct(rs.get('ranging', 0))} | "
            f"{pct(rs.get('trending_up', 0))} | "
            f"{pct(rs.get('trending_down', 0))} | "
            f"{pct(rs.get('high_volatility', 0))} |"
        )
    B("")
    B("## D1 monthly board")
    B("")
    B(
        "| Month | Dominant regime | meanrev | trendfollow | Bars | "
        "ranging | trend↑ | trend↓ | high_vol |"
    )
    B("| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |")
    for r in d1_rows:
        rs = r["regime_shares"]
        B(
            f"| {r['month']} | {r['dominant_regime']} | "
            f"**{r.get('meanrev_tag')}** | **{r.get('trendfollow_tag')}** | "
            f"{r['bar_count']} | {pct(rs.get('ranging', 0))} | "
            f"{pct(rs.get('trending_up', 0))} | "
            f"{pct(rs.get('trending_down', 0))} | "
            f"{pct(rs.get('high_volatility', 0))} |"
        )
    B("")
    B("## Audit takeaways")
    B("")
    B(
        f"1. **H1 meanrev MATCH in {mr_match}/{n_h1} months** vs trendfollow "
        f"MATCH in {tf_match}/{n_h1} — modal H1 month regime is "
        f"**{modal[0]}** ({modal[1]}/{n_h1})."
    )
    if fragile:
        B(
            f"2. **Fragile months:** {', '.join(fragile)} "
            "(high_vol-dominant → both families FRAGILE)."
        )
    else:
        B("2. **Fragile months:** none in the confirmed H1 board.")
    if trend_months:
        B(
            f"3. **Trendfollow MATCH months:** {', '.join(trend_months)} "
            "(ex-post; not forward signals)."
        )
    else:
        B("3. **Trendfollow MATCH months:** none in this window.")
    if st:
        B(
            f"4. **Live gate vs nowcast:** confirmed H1={st['regime']} "
            f"(conf {fnum(st['confidence'], 3)}) while 30d shares tag "
            f"meanrev={fit30['meanrev']['tag']} / "
            f"trendfollow={fit30['trendfollow']['tag']} — use 30d shares "
            "for the research gate, not the single-bar confirmed label alone."
        )
    else:
        B(
            "4. **Live gate vs character:** use 30d shares for the research "
            "gate when state is missing."
        )
    B(
        "5. **Partial / missing months:** regime warmup and broker gaps "
        "(e.g. thin May 2026, missing Jun 2026 bars) can drop months from "
        "confirmed boards."
    )
    B(
        "6. Monthly MATCH is **ex-post**, not a forward signal. Live research "
        "gate should use nowcast + 30d shares, not calendar-month prophecy."
    )
    B("")
    B(d["disclaimer"])
    B("")
    (out / "regime-audit.md").write_text("\n".join(L), encoding="utf-8")

    (out / "profile.json").write_text(json.dumps(prof, indent=2), encoding="utf-8")

    canvas_link = (
        "/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/"
        "canvases/msft-asset-profile.canvas.tsx"
    )
    readme = f"""# MSFT research dossier

Living asset profile + 2-year monthly regime / fit audit produced from the local Ouroboros pipe.

| File | Contents |
| --- | --- |
| [`PROFILE.md`](./PROFILE.md) | Comprehensive asset profile (identity, clocks, character, path, narrative) |
| [`regime-audit.md`](./regime-audit.md) | Monthly H1/D1 regime shares + MATCH/MISMATCH/FRAGILE tags |
| [`profile.json`](./profile.json) | `profile.v1` snapshot |
| [`audit.json`](./audit.json) | Full machine export (boards, nowcast, news) |

**Canvas cover:** [{canvas_link.split('/')[-1]}]({canvas_link}) — open beside chat.

Models: `{d['models']['regime']}` · `{d['models']['fit']}` · `{d['models']['profile']}`  
Range: {dr['d1_start'][:10]} → {dr['d1_end'][:10]} · regenerated via `server/scripts/msft_regime_audit.py`
"""
    (out / "README.md").write_text(readme, encoding="utf-8")
    print("wrote", out)
    for f in sorted(out.iterdir()):
        print(f"  {f.name} {f.stat().st_size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
