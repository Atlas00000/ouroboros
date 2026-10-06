import {
  cssVarForTone,
  REGIME_LABEL,
  toneForRegime,
  type Regime,
  type SemanticTone,
} from "@/design/map/backend-visual";

export type NowcastProb = {
  regime: string;
  probability: number;
  pct: number;
  label: string;
  tone: SemanticTone;
  color: string;
};

export function buildNowcastProbs(
  rows: { regime: string; probability: number }[] | undefined | null,
): NowcastProb[] {
  if (!rows?.length) return [];
  return rows
    .filter((r) => Number.isFinite(r.probability) && r.probability > 0)
    .map((r) => {
      const tone = toneForRegime(r.regime as Regime);
      return {
        regime: r.regime,
        probability: r.probability,
        pct: Math.round(r.probability * 1000) / 10,
        label: REGIME_LABEL[r.regime] ?? r.regime.replaceAll("_", " "),
        tone,
        color: cssVarForTone(tone),
      };
    })
    .sort((a, b) => b.probability - a.probability);
}

export function formatProbPct(pct: number): string {
  return `${pct.toFixed(pct % 1 === 0 ? 0 : 1)}%`;
}

export function nowcastFocusBlurb(row: NowcastProb, activeRegime: string): string {
  const isLive = row.regime === activeRegime;
  if (isLive && row.pct >= 50) {
    return `Live soft probability leans hard into ${row.label}. This is the nowcast, not the history book.`;
  }
  if (isLive) {
    return `${row.label} is the active regime badge, with ${formatProbPct(row.pct)} soft probability in the current cut.`;
  }
  return `${row.label} carries ${formatProbPct(row.pct)} of the live probability mass. Not confirmed history.`;
}
