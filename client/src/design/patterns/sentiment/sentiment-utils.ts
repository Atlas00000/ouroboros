export type SentimentPolarity = "bullish" | "bearish" | "neutral";

export type SentimentDriverRow = {
  id: string;
  title: string;
  contribution: number | null;
  source: string | null;
  url: string | null;
  published_at: string | null;
};

export function sentimentPolarity(score: number): SentimentPolarity {
  if (score >= 0.15) return "bullish";
  if (score <= -0.15) return "bearish";
  return "neutral";
}

export function polarityLabel(p: SentimentPolarity): string {
  if (p === "bullish") return "Constructive";
  if (p === "bearish") return "Pressured";
  return "Balanced";
}

export function polarityTone(p: SentimentPolarity): string {
  if (p === "bullish") return "var(--ds-ok)";
  if (p === "bearish") return "var(--ds-halt)";
  return "var(--ds-idle)";
}

export function formatScore(score: number): string {
  const sign = score > 0 ? "+" : "";
  return `${sign}${score.toFixed(2)}`;
}

/** Map score [-1,1] → percent along bipolar track [0,100]. */
export function scoreToPct(score: number): number {
  const clamped = Math.max(-1, Math.min(1, score));
  return ((clamped + 1) / 2) * 100;
}

/** Absolute pressure 0–100 for dial fill. */
export function scoreMagnitudePct(score: number): number {
  return Math.max(0, Math.min(100, Math.abs(score) * 100));
}

export function buildDriverRows(
  drivers:
    | {
        title: string;
        url?: string | null;
        published_at?: string | null;
        contribution?: number | null;
        source?: string | null;
      }[]
    | undefined
    | null,
): SentimentDriverRow[] {
  if (!drivers?.length) return [];
  return drivers.slice(0, 5).map((d, i) => ({
    id: `${i}-${d.title.slice(0, 24)}`,
    title: d.title,
    contribution: d.contribution ?? null,
    source: d.source ?? null,
    url: d.url ?? null,
    published_at: d.published_at ?? null,
  }));
}

export function sentimentFocusBlurb(
  score: number,
  polarity: SentimentPolarity,
  itemCount: number,
  windowHours: number,
): string {
  const label = polarityLabel(polarity);
  return `${label} cut at ${formatScore(score)} from ${itemCount} scored items over ${windowHours}h. Decay weighted aggregate on [-1, +1].`;
}

export function driverFocusBlurb(row: SentimentDriverRow): string {
  const c =
    row.contribution == null
      ? "unweighted"
      : formatScore(row.contribution);
  const src = row.source ?? "desk source";
  return `${src} · contribution ${c}. One of the headlines pulling the live score.`;
}
