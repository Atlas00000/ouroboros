/**
 * Backend enums → design-system tone tokens.
 * Keep names aligned with UI_PHILOSOPHY.md.
 */

export type SemanticTone = "signal" | "ok" | "warn" | "halt" | "idle" | "vol" | "faint";

export type Regime = "trending_up" | "trending_down" | "ranging" | "high_volatility" | string;

/** Market regime → Badge / colour tone */
export function toneForRegime(regime?: Regime | null): SemanticTone {
  switch (regime) {
    case "trending_up":
      return "ok";
    case "trending_down":
      return "halt";
    case "high_volatility":
      return "vol";
    case "ranging":
      return "idle";
    default:
      return "faint";
  }
}

export const REGIME_LABEL: Record<string, string> = {
  trending_up: "Up",
  trending_down: "Down",
  ranging: "Range",
  high_volatility: "High vol",
};

/** Freshness / provenance */
export function toneForStale(stale?: boolean | null): SemanticTone {
  return stale ? "warn" : "ok";
}

/** Feed / source registry status strings from API */
export function toneForFeedStatus(status?: string | null): SemanticTone {
  const s = (status ?? "").toLowerCase();
  if (s === "ok" || s === "healthy" || s === "live") return "ok";
  if (s === "stale" || s === "degraded" || s === "lagging") return "warn";
  if (s === "error" || s === "down" || s === "failed") return "halt";
  return "idle";
}

/**
 * Reserved: zone codes from future / sibling systems.
 * Maps unknown zones to idle so pages can wire early without inventing colours.
 */
export function toneForZone(zone?: string | null): SemanticTone {
  const z = (zone ?? "").toLowerCase();
  if (z === "core" || z === "primary") return "signal";
  if (z === "risk" || z === "hot") return "vol";
  if (z === "blocked" || z === "halt") return "halt";
  return "idle";
}

/** Reserved: asset / pipeline lifecycle */
export function toneForLifecycle(phase?: string | null): SemanticTone {
  const p = (phase ?? "").toLowerCase();
  if (p === "active" || p === "live" || p === "ready") return "ok";
  if (p === "warming" || p === "pending" || p === "cooldown") return "warn";
  if (p === "retired" || p === "disabled" || p === "failed") return "halt";
  return "idle";
}

/** Reserved: gate decisions (allow / skip) */
export function toneForGate(decision?: string | null): SemanticTone {
  const d = (decision ?? "").toLowerCase();
  if (d === "allow" || d === "pass" || d === "enter") return "ok";
  if (d === "skip" || d === "hold" || d === "wait") return "idle";
  if (d === "deny" || d === "block" || d === "reject") return "halt";
  return "faint";
}

/** Regime fit tags (MATCH / MISMATCH / FRAGILE) */
export function toneForFitTag(tag?: string | null): SemanticTone {
  const t = (tag ?? "").toUpperCase();
  if (t === "MATCH") return "ok";
  if (t === "MISMATCH") return "halt";
  if (t === "FRAGILE") return "warn";
  return "faint";
}

/** CSS custom property helpers for charts / inline styles */
export function cssVarForTone(tone: SemanticTone): string {
  switch (tone) {
    case "signal":
      return "var(--ds-signal)";
    case "ok":
      return "var(--ds-ok)";
    case "warn":
      return "var(--ds-warn)";
    case "halt":
      return "var(--ds-halt)";
    case "vol":
      return "var(--ds-vol)";
    case "idle":
      return "var(--ds-idle)";
    case "faint":
    default:
      return "var(--ds-ink-faint)";
  }
}
