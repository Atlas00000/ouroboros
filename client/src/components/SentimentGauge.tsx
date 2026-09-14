/** Compact sentiment score for dashboard cards (full gauge in W10). */

import { cn } from "@/lib/utils";

export function SentimentGauge({ score }: { score?: number | null }) {
  if (score == null || Number.isNaN(score)) {
    return <span className="tabular-nums text-[11px] text-muted">sent —</span>;
  }
  const tone =
    score > 0.15
      ? "text-regime-trending-up"
      : score < -0.15
        ? "text-regime-trending-down"
        : "text-muted";
  return (
    <span className={cn("tabular-nums text-[11px] font-medium", tone)}>
      {score >= 0 ? "+" : ""}
      {score.toFixed(2)}
    </span>
  );
}
