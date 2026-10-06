import {
  buildDriverRows,
  formatScore,
  polarityLabel,
  polarityTone,
  sentimentPolarity,
  type SentimentDriverRow,
  type SentimentPolarity,
} from "@/design/patterns/sentiment/sentiment-utils";

export type { SentimentDriverRow as DriverRow, SentimentPolarity };

export {
  buildDriverRows,
  formatScore,
  polarityLabel,
  polarityTone,
  sentimentPolarity,
};

export function driverPolarity(row: SentimentDriverRow): SentimentPolarity {
  return sentimentPolarity(row.contribution ?? 0);
}

export function driverHeatLabel(row: SentimentDriverRow): string {
  if (row.contribution == null) return "Unweighted";
  return polarityLabel(driverPolarity(row));
}

export function formatPublished(iso: string | null): string | null {
  if (!iso) return null;
  const d = iso.slice(0, 10);
  const t = iso.includes("T") ? iso.slice(11, 16) : "";
  return t ? `${d} ${t}Z` : d;
}

export function driverLeadBlurb(row: SentimentDriverRow): string {
  const heat = driverHeatLabel(row);
  const src = row.source ?? "desk source";
  const c =
    row.contribution == null ? "n/a" : formatScore(row.contribution);
  return `${src} · ${heat} pull · contribution ${c}. Research headline feeding the live sentiment cut.`;
}

export function dominantDriverPolarity(
  rows: SentimentDriverRow[],
): SentimentPolarity {
  if (!rows.length) return "neutral";
  let sum = 0;
  let n = 0;
  for (const r of rows) {
    if (r.contribution == null) continue;
    sum += r.contribution;
    n += 1;
  }
  if (!n) return "neutral";
  return sentimentPolarity(sum / n);
}
