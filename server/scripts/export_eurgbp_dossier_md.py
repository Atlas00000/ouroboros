"""Render research/assets/EURGBP markdown from audit.json."""

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


def _share_map(rd: list[dict]) -> dict[str, float]:
    return {r["regime"]: float(r["share"]) for r in rd}


def _fit_interp(fit30: dict) -> str:
    mr = fit30["meanrev"]
    tf = fit30["trendfollow"]
    mr_s = mr["shares"]
    rs = mr.get("regime_shares") or {}
    lead = max(rs.items(), key=lambda kv: kv[1])[0] if rs else "mixed"
    frag = float(mr_s.get("FRAGILE") or 0) * 100
    return (
        f"Interpretation: last ~30d H1 mass is **{lead}-led** → meanrev "
        f"**{mr['tag']}**, trendfollow **{tf['tag']}**. "
        f"FRAGILE share ≈ {frag:.0f}%."
    )


def _character_read(rd: list[dict], asset_class: str) -> str:
    sm = _share_map(rd)
    ranging = sm.get("ranging", 0) * 100
    hv = sm.get("high_volatility", 0) * 100
    up = sm.get("trending_up", 0) * 100
    down = sm.get("trending_down", 0) * 100
    net_trend = up + down
    lean = "meanrev-leaning" if ranging >= net_trend else "trend-leaning"
    return (
        f"**Read:** ranging ({ranging:.0f}%) + high_volatility ({hv:.0f}%) · "
        f"net trending (up+down) ≈ {net_trend:.0f}%. "
        f"This is a **{lean}** "
        f"{'FX cross' if asset_class == 'fx' else asset_class} on H1 history"
        + (" — with a material fragile/high-vol sleeve." if hv >= 20 else ".")
    )


def _corr_blurb(corrs: list[dict]) -> str:
    if not corrs:
        return "No peer correlations in this window (depth / peer matrix empty)."
    ranked = sorted(corrs, key=lambda c: abs(float(c["coefficient"])), reverse=True)
    top = ranked[:4]
    parts = [f"{c['symbol']} ({float(c['coefficient']):+.2f})" for c in top]
    negs = [c for c in ranked if float(c["coefficient"]) < -0.15]
    neg_txt = (
        " Notable negatives: "
        + ", ".join(f"{c['symbol']} ({float(c['coefficient']):+.2f})" for c in negs[:3])
        + "."
        if negs
        else ""
    )
    return f"Strongest |ρ| peers: {', '.join(parts)}.{neg_txt}"


def _event_blurb(events: list[dict]) -> str:
    if not events:
        return (
            "No event taxonomy on profile — honest gap until calendar "
            "sensitivities are scored for this FX cross."
        )
    types = [e.get("event_type") or "?" for e in events]
    atrs = [e.get("typical_move_atr_multiple") for e in events]
    filled = [a for a in atrs if a is not None]
    if not filled:
        return (
            f"Taxonomy present ({' / '.join(types)}) but **ATR multiples empty** — "
            "calendar hits scored below the ≥3-window gate. Honest gap until "
            "event windows are scored."
        )
    bits = []
    for e in events:
        atr = e.get("typical_move_atr_multiple")
        bits.append(
            f"{e.get('event_type')}: {float(atr):.2f}× ATR"
            if atr is not None
            else f"{e.get('event_type')}: —"
        )
    return "Event move multiples: " + "; ".join(bits) + "."


def _fragile_clusters(h1_rows: list[dict]) -> list[str]:
    clusters: list[str] = []
    run: list[str] = []
    for r in h1_rows:
        if r.get("meanrev_tag") == "FRAGILE" and r.get("trendfollow_tag") == "FRAGILE":
            run.append(r["month"])
        else:
            if len(run) >= 2:
                clusters.append(f"{run[0]}–{run[-1]}")
            run = []
    if len(run) >= 2:
        clusters.append(f"{run[0]}–{run[-1]}")
    return clusters


def _trend_match_months(h1_rows: list[dict]) -> list[str]:
    return [
        r["month"]
        for r in h1_rows
        if r.get("trendfollow_tag") == "MATCH" and r.get("dominant_regime") in (
            "trending_up",
            "trending_down",
        )
    ]


def main() -> int:
    repo = Path(__file__).resolve().parents[2]
    out = repo / "research" / "assets" / "EURGBP"
    d = json.loads((out / "audit.json").read_text(encoding="utf-8"))
    prof = d["profile"]
    nc = d["nowcast"]
    dr = d["data_range"]
    id_ = prof["identity"]
    vol = prof["volatility"]
    liq = prof["liquidity"]
    hours = prof["trading_hours"]
    rd = prof["regime_distribution"]
    events = prof.get("event_sensitivities") or []
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
    mr_m = tsum.get("H1|meanrev", {}).get("MATCH", 0)
    tf_m = tsum.get("H1|trendfollow", {}).get("MATCH", 0)
    modal = dom_h1.most_common(1)[0] if dom_h1 else ("?", 0)
    frag_c = _fragile_clusters(h1_rows)
    trend_ms = _trend_match_months(h1_rows)

    lines: list[str] = []
    A = lines.append
    A("# EURGBP — Asset profile dossier")
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
        "`canvases/eurgbp-asset-profile.canvas.tsx` in the Cursor project."
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
        A("_No H1 state row in pipe._")
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
    quote = id_.get("quote_currency") or "GBP"
    A(
        f"| Typical daily range | {fnum(vol['typical_daily_range'], 5)} "
        f"{quote} |"
    )
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
    A(_character_read(rd, id_.get("asset_class") or "fx"))
    A("")
    A("### Peer correlations (H1 ~30d)")
    A("")
    A("| Peer | ρ |")
    A("| --- | ---: |")
    for c in prof["correlations"]:
        A(f"| {c['symbol']} | {c['coefficient']:+.3f} |")
    A("")
    A(_corr_blurb(prof["correlations"]))
    A("")
    A("### Event sensitivities")
    A("")
    A(_event_blurb(events))
    A("")
    A("---")
    A("")
    A("## Path")
    A("")
    A(
        f"Monthly D1 path return over the window: **{tot_ret:+.1f}%** "
        f"(open {px[0]['open']:.5f} → last close {px[-1]['close']:.5f})."
    )
    A("")
    A("| Month | Ret % | Close |")
    A("| --- | ---: | ---: |")
    for r in px:
        A(f"| {r['month']} | {r['ret_pct']:+.2f} | {r['close']:.5f} |")
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
    else:
        A("- Sentiment: _none in pipe_")
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
    if not d["recent_news"]:
        A("- _(no mapped headlines)_")
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
    B("# EURGBP — Regime audit & fit tagging (monthly, 2y)")
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
        f"1. **H1 meanrev MATCH in {mr_m}/{n_h1} months** vs trendfollow MATCH "
        f"in {tf_m}/{n_h1} — modal H1 month regime is `{modal[0]}` "
        f"({modal[1]}/{n_h1})."
    )
    if frag_c:
        B(
            f"2. **Fragile clusters** (both families FRAGILE): {', '.join(frag_c)}."
        )
    else:
        B(
            "2. **Fragile months** are present but do not form long consecutive "
            "clusters on H1."
        )
    if trend_ms:
        B(
            f"3. **Trend MATCH months** (dominant trending_*): "
            f"{', '.join(trend_ms)}."
        )
    else:
        B(
            "3. **Trend MATCH months** with a trending_* dominant regime are "
            "scarce in this window."
        )
    B(
        "4. **TF disagreement is expected** when dominant regime is ranging but "
        "trend shares outvote ranging on the fit map (or the reverse)."
    )
    B(
        f"5. First/last months may be thin after regime warmup "
        f"({dr['months'][0]} / {dr['months'][-1]})."
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

    readme = f"""# EURGBP research dossier

Living asset profile + 2-year monthly regime / fit audit produced from the local Ouroboros pipe.

| File | Contents |
| --- | --- |
| [`PROFILE.md`](./PROFILE.md) | Comprehensive asset profile (identity, clocks, character, path, narrative) |
| [`regime-audit.md`](./regime-audit.md) | Monthly H1/D1 regime shares + MATCH/MISMATCH/FRAGILE tags |
| [`profile.json`](./profile.json) | `profile.v1` snapshot |
| [`audit.json`](./audit.json) | Full machine export (boards, nowcast, news) |

**Canvas cover:** [eurgbp-asset-profile.canvas.tsx](/Users/emili/.cursor/projects/c-Users-emili-OneDrive-Desktop-Ouroboros/canvases/eurgbp-asset-profile.canvas.tsx) — open beside chat.

Models: `{d['models']['regime']}` · `{d['models']['fit']}` · `{d['models']['profile']}`  
Range: {dr['d1_start'][:10]} → {dr['d1_end'][:10]} · regenerated via `server/scripts/eurgbp_regime_audit.py`
"""
    (out / "README.md").write_text(readme, encoding="utf-8")
    print("wrote", out)
    for f in sorted(out.iterdir()):
        print(f"  {f.name} {f.stat().st_size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
