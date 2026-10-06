import {
  cssVarForTone,
  REGIME_LABEL,
  toneForRegime,
  type Regime,
  type SemanticTone,
} from "@/design/map/backend-visual";

export type RegimeShareRow = {
  regime: string;
  share: number;
  pct: number;
  label: string;
  tone: SemanticTone;
  color: string;
};

export function buildRegimeShares(
  rows: { regime: string; share: number }[] | undefined | null,
): RegimeShareRow[] {
  if (!rows?.length) return [];
  return rows
    .filter((r) => Number.isFinite(r.share) && r.share > 0)
    .map((r) => {
      const tone = toneForRegime(r.regime as Regime);
      return {
        regime: r.regime,
        share: r.share,
        pct: Math.round(r.share * 1000) / 10,
        label: REGIME_LABEL[r.regime] ?? r.regime.replaceAll("_", " "),
        tone,
        color: cssVarForTone(tone),
      };
    })
    .sort((a, b) => b.share - a.share);
}

export function dominantShare(rows: RegimeShareRow[]): RegimeShareRow | null {
  return rows[0] ?? null;
}

/** How concentrated the history book is. */
export function historyConcentration(
  lead: RegimeShareRow | null,
): "dominant" | "lean" | "mixed" {
  if (!lead) return "mixed";
  if (lead.pct >= 55) return "dominant";
  if (lead.pct >= 35) return "lean";
  return "mixed";
}

export function concentrationLabel(
  c: "dominant" | "lean" | "mixed",
): string {
  if (c === "dominant") return "Dominant past";
  if (c === "lean") return "Leaning past";
  return "Mixed past";
}

export function historyFocusBlurb(row: RegimeShareRow): string {
  if (row.pct >= 55) {
    return `${row.label} took most of the confirmed history share in this profile cut.`;
  }
  if (row.pct >= 35) {
    return `${row.label} leads the history book but other regimes still claim meaningful time.`;
  }
  if (row.pct >= 15) {
    return `${row.label} is a visible slice of history. The book is relatively balanced.`;
  }
  return `${row.label} is a thin slice of confirmed regime history for this instrument.`;
}

export function formatSharePct(pct: number): string {
  return `${pct.toFixed(pct % 1 === 0 ? 0 : 1)}%`;
}
