import { StaleBadge } from "@/components/StaleBadge";
import type { Insight } from "@/lib/queries/asset-detail";

export function InsightFeed({ insight }: { insight: Insight | null }) {
  if (!insight) {
    return (
      <section className="rounded-md border border-border bg-card p-3">
        <h2 className="text-sm font-medium">Insights</h2>
        <p className="mt-2 text-sm text-muted">No narrative insight yet.</p>
      </section>
    );
  }

  return (
    <section className="rounded-md border border-border bg-card p-3">
      <div className="flex flex-wrap items-center gap-2">
        <h2 className="text-sm font-medium">Insights</h2>
        <span className="rounded bg-border px-1.5 py-0.5 text-[10px] uppercase tracking-wide text-muted">
          {insight.type || "narrative"}
        </span>
        <StaleBadge stale={insight.provenance.stale} />
      </div>
      <h3 className="mt-3 text-sm font-medium text-foreground">{insight.title}</h3>
      <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed text-muted">{insight.body}</p>
      {insight.tags?.length ? (
        <p className="mt-3 text-[10px] text-muted">{insight.tags.join(" · ")}</p>
      ) : null}
      <p className="mt-4 border-t border-border pt-3 text-[11px] leading-snug text-muted">
        {insight.disclaimer?.text ||
          "Ouroboros provides internal research context only. Outputs are not investment advice and do not execute trades."}
      </p>
      <p className="mt-2 text-[10px] text-muted">
        {insight.provenance.model_version} · as of {insight.as_of}
      </p>
    </section>
  );
}
