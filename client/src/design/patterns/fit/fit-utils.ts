import { cssVarForTone, toneForFitTag } from "@/design/map/backend-visual";
import type { EdgeFamily, FitSnapshot, FitTag } from "@/lib/api/types";

export type FitShareRow = {
  tag: FitTag;
  share: number;
  pct: number;
  color: string;
  label: string;
};

export type FitFamilyOption = {
  id: EdgeFamily;
  label: string;
  short: string;
};

export const FIT_FAMILIES: FitFamilyOption[] = [
  { id: "meanrev", label: "Mean reversion", short: "Mean-rev" },
  { id: "trendfollow", label: "Trend follow", short: "Trend" },
];

export const FIT_TAG_ORDER: FitTag[] = ["MATCH", "MISMATCH", "FRAGILE"];

export const FIT_TAG_COPY: Record<
  FitTag,
  { label: string; blurb: string }
> = {
  MATCH: {
    label: "Match",
    blurb: "Environment fits this family's home cell for the decision TF.",
  },
  MISMATCH: {
    label: "Mismatch",
    blurb: "Kill or adverse regime for this family — research gate prefers off.",
  },
  FRAGILE: {
    label: "Fragile",
    blurb: "Event or vol-cluster caution — size or pause, not a hard kill.",
  },
};

export function formatSharePct(share: number): string {
  if (!Number.isFinite(share)) return "—";
  return `${Math.round(share * 100)}%`;
}

export function formatRegimeLabel(regime?: string | null): string {
  if (!regime) return "—";
  return regime.replaceAll("_", " ");
}

export function familyLabel(family: EdgeFamily | string | undefined): string {
  const hit = FIT_FAMILIES.find((f) => f.id === family);
  return hit?.label ?? String(family ?? "—");
}

/** Build share rows from fit.v1 shares; fill missing tags at 0 for a stable triad. */
export function buildShareRows(
  shares?: Record<string, number> | null,
): FitShareRow[] {
  const map = new Map<string, number>();
  if (shares) {
    for (const [k, v] of Object.entries(shares)) {
      const tag = k.toUpperCase() as FitTag;
      if (FIT_TAG_ORDER.includes(tag) && Number.isFinite(v)) {
        map.set(tag, Math.max(0, Math.min(1, v)));
      }
    }
  }
  return FIT_TAG_ORDER.map((tag) => {
    const share = map.get(tag) ?? 0;
    return {
      tag,
      share,
      pct: Math.round(share * 100),
      color: cssVarForTone(toneForFitTag(tag)),
      label: FIT_TAG_COPY[tag].label,
    };
  });
}

export function fitToneCss(tag?: FitTag | string | null): string {
  return cssVarForTone(toneForFitTag(tag));
}

export function dominantShare(rows: FitShareRow[]): FitShareRow | null {
  if (!rows.length) return null;
  return rows.reduce((a, b) => (b.share > a.share ? b : a));
}

export function snapshotHasShares(snap: FitSnapshot | null): boolean {
  return Boolean(snap?.shares && Object.keys(snap.shares).length);
}
