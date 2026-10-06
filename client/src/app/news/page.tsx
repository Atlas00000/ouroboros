import Link from "next/link";

import { StaleBadge } from "@/components/StaleBadge";
import { EmptyState } from "@/components/ui/PageState";
import { NewsImpactBars } from "@/design/patterns/news";
import { AppShell } from "@/design/shells/AppShell";
import { PageHeader } from "@/design/shells/PageHeader";
import { Surface } from "@/design/primitives/Surface";
import { Text } from "@/design/primitives/Text";
import { fetchNewsServer } from "@/lib/queries/server";

export const dynamic = "force-dynamic";

export default async function NewsPage() {
  const news = await fetchNewsServer(50);

  return (
    <AppShell wide>
      <PageHeader
        title="News"
        description="Headlines and calendar context. Use when sentiment is quiet or a story needs the raw narrative layer."
        meta={<StaleBadge stale={news?.provenance.stale} />}
      />

      {!news?.items.length ? (
        <EmptyState title="No news items">
          Ensure the API is up and{" "}
          <code className="font-mono text-ds-ink">OUROBOROS_SERVER_API_KEY</code> is set for SSR.
        </EmptyState>
      ) : (
        <div className="flex flex-col gap-6">
          <NewsImpactBars items={news.items} />
          <Surface tone="plane" border="hairline" pad="none" className="overflow-hidden">
            <ul className="divide-y divide-ds-line">
              {news.items.map((n) => (
                <li key={n.id} className="px-4 py-3">
                  <div className="flex flex-wrap items-baseline justify-between gap-2">
                    {n.symbol ? (
                      <Link
                        href={`/assets/${n.symbol}`}
                        className="text-sm text-ds-ink hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ds-signal"
                      >
                        {n.headline}
                      </Link>
                    ) : (
                      <Text as="p" variant="body">
                        {n.headline}
                      </Text>
                    )}
                    {n.impact ? (
                      <Text as="span" variant="micro">
                        {n.impact}
                      </Text>
                    ) : null}
                  </div>
                  <Text as="p" variant="micro" className="mt-1 normal-case tracking-normal">
                    {n.source}
                    {n.symbol ? ` · ${n.symbol}` : ""}
                    {n.published_at ? ` · ${n.published_at}` : ""}
                  </Text>
                </li>
              ))}
            </ul>
          </Surface>
        </div>
      )}
    </AppShell>
  );
}
