/** Session name → approximate UTC open window (hour, wrap allowed). Research heuristic. */
const SESSION_UTC_WINDOWS: Record<string, { start: number; end: number }> = {
  sydney: { start: 21, end: 6 },
  tokyo: { start: 0, end: 9 },
  london: { start: 7, end: 16 },
  new_york: { start: 12, end: 21 },
  newyork: { start: 12, end: 21 },
  ny: { start: 12, end: 21 },
};

export function normalizeSessionKey(name: string): string {
  return name.trim().toLowerCase().replace(/[\s-]+/g, "_").replace(/_+/g, "_");
}

export function sessionIsLiveUtc(name: string, utcHour: number): boolean {
  const raw = name.trim().toLowerCase();
  const underscored = raw.replace(/[\s-]+/g, "_");
  const compact = underscored.replace(/_/g, "");
  const win =
    SESSION_UTC_WINDOWS[underscored] ||
    SESSION_UTC_WINDOWS[compact] ||
    SESSION_UTC_WINDOWS[raw];
  if (!win) return false;
  if (win.start <= win.end) {
    return utcHour >= win.start && utcHour < win.end;
  }
  return utcHour >= win.start || utcHour < win.end;
}

export function formatProfileTime(value?: string | null): string | null {
  if (!value) return null;
  const m = String(value).match(/(\d{2}):(\d{2})/);
  return m ? `${m[1]}:${m[2]}` : String(value);
}

export function formatAsOfShort(iso?: string | null): string {
  if (!iso) return "—";
  const d = iso.slice(0, 10);
  const t = iso.includes("T") ? iso.slice(11, 16) : "";
  return t ? `${d} ${t}Z` : d;
}

export type ProfileMeterId = "atr" | "rv" | "range";

export type ProfileHeat = "calm" | "warm" | "hot";

export type ProfileMeter = {
  id: ProfileMeterId;
  label: string;
  unit: string;
  value: number | null;
  blurb: string;
};

export function profileHeat(profile: {
  volatility?: {
    atr_percentile_30d?: number | null;
    realized_vol_percentile_30d?: number | null;
  } | null;
}): ProfileHeat {
  const atr = profile.volatility?.atr_percentile_30d;
  const rv = profile.volatility?.realized_vol_percentile_30d;
  const peak = Math.max(
    atr == null || Number.isNaN(atr) ? 0 : atr,
    rv == null || Number.isNaN(rv) ? 0 : rv,
  );
  if (peak >= 75) return "hot";
  if (peak >= 45) return "warm";
  return "calm";
}

export function profileHeatLabel(heat: ProfileHeat): string {
  if (heat === "hot") return "Elevated vol";
  if (heat === "warm") return "Building";
  return "Contained";
}

export function buildProfileMeters(profile: {
  volatility?: {
    atr_percentile_30d?: number | null;
    realized_vol_percentile_30d?: number | null;
  } | null;
  liquidity?: {
    spread_percentile_30d?: number | null;
    notes?: string | null;
  } | null;
}): ProfileMeter[] {
  const liqNote = profile.liquidity?.notes?.trim();
  return [
    {
      id: "atr",
      label: "ATR",
      unit: "pct 30d",
      value: profile.volatility?.atr_percentile_30d ?? null,
      blurb: "Average true range percentile over ~30 days of D1 history.",
    },
    {
      id: "rv",
      label: "RV",
      unit: "pct 30d",
      value: profile.volatility?.realized_vol_percentile_30d ?? null,
      blurb: "Realized volatility percentile — same 30d window, return-based.",
    },
    {
      id: "range",
      label: "Range",
      unit: "pct 30d",
      value: profile.liquidity?.spread_percentile_30d ?? null,
      blurb:
        liqNote ||
        "High–low range percentile used as liquidity proxy until true bid/ask lands.",
    },
  ];
}
