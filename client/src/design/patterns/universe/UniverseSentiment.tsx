import { cn } from "@/lib/utils";

type UniverseSentimentProps = {
  score?: number | null;
  className?: string;
};

/** Signed sentiment mark — typography + tone, no gauge chrome. */
export function UniverseSentiment({ score, className }: UniverseSentimentProps) {
  if (score == null || Number.isNaN(score)) {
    return (
      <span className={cn("ds-universe-sent", className)} data-tone="idle">
        sent —
      </span>
    );
  }

  const tone = score > 0.15 ? "ok" : score < -0.15 ? "halt" : "idle";
  const sign = score > 0 ? "+" : "";

  return (
    <span className={cn("ds-universe-sent", className)} data-tone={tone}>
      {sign}
      {score.toFixed(2)}
    </span>
  );
}
