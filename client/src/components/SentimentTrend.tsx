import { SentimentGauge } from "@/components/SentimentGauge";
import { StaleBadge } from "@/components/StaleBadge";
import type { SentimentSnapshot } from "@/lib/queries/asset-detail";

export function SentimentTrend({ sentiment }: { sentiment: SentimentSnapshot | null }) {
  if (!sentiment) {
    return (
      <section className="rounded-md border border-border bg-card p-3">
        <h2 className="text-sm font-medium">Sentiment</h2>
        <p className="mt-2 text-sm text-muted">No sentiment in the current window.</p>
      </section>
    );
  }

  const score = sentiment.score;
  const left = Math.round(((score + 1) / 2) * 100);

  return (
    <section className="rounded-md border border-border bg-card p-3">
      <div className="flex items-center gap-2">
        <h2 className="text-sm font-medium">Sentiment</h2>
        <StaleBadge stale={sentiment.provenance.stale} />
        <SentimentGauge score={score} />
      </div>
      <div className="relative mt-4 h-2 rounded bg-border">
        <div
          className="absolute top-1/2 h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full border border-border bg-foreground"
          style={{ left: `${left}%` }}
        />
      </div>
      <div className="mt-1 flex justify-between text-[10px] text-muted">
        <span>-1</span>
        <span>0</span>
        <span>+1</span>
      </div>
      <p className="mt-3 text-[10px] text-muted">
        {sentiment.item_count} items · {sentiment.window_hours}h window · as of {sentiment.as_of}
      </p>
    </section>
  );
}
