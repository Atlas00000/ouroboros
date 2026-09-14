import Link from "next/link";

import { AppShell } from "@/components/AppShell";
import { StaleBadge } from "@/components/StaleBadge";
import { EmptyState } from "@/components/ui/PageState";
import { fetchNewsServer } from "@/lib/queries/server";

export const dynamic = "force-dynamic";

export default async function NewsPage() {
  const news = await fetchNewsServer(50);

  return (
    <AppShell>
      <div className="flex flex-wrap items-center gap-2">
        <h1 className="text-lg font-semibold tracking-tight">News</h1>
        <StaleBadge stale={news?.provenance.stale} />
      </div>
      <p className="text-sm text-muted">
        Headlines and calendar items. Use when sentiment is empty because feeds went quiet.
      </p>

      {!news?.items.length ? (
        <EmptyState title="No news items">
          Ensure the API is up and{" "}
          <code className="font-mono text-foreground">OUROBOROS_SERVER_API_KEY</code> is set for
          SSR.
        </EmptyState>
      ) : (
        <ul className="divide-y divide-border rounded-md border border-border bg-card">
          {news.items.map((n) => (
            <li key={n.id} className="px-4 py-3">
              <div className="flex flex-wrap items-baseline justify-between gap-2">
                {n.symbol ? (
                  <Link
                    href={`/assets/${n.symbol}`}
                    className="text-sm text-foreground hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
                  >
                    {n.headline}
                  </Link>
                ) : (
                  <p className="text-sm text-foreground">{n.headline}</p>
                )}
                {n.impact ? (
                  <span className="text-[10px] uppercase tracking-wide text-muted">{n.impact}</span>
                ) : null}
              </div>
              <p className="mt-1 text-[11px] text-muted">
                {n.source}
                {n.symbol ? ` · ${n.symbol}` : ""}
                {n.published_at ? ` · ${n.published_at}` : ""}
              </p>
            </li>
          ))}
        </ul>
      )}
    </AppShell>
  );
}
