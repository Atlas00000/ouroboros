import Link from "next/link";

import { AppShell } from "@/components/AppShell";
import { CorrelationHeatmap } from "@/components/CorrelationHeatmap";
import { DriverHeadlines } from "@/components/DriverHeadlines";
import { InsightFeed } from "@/components/InsightFeed";
import { PriceChart } from "@/components/PriceChart";
import { ProfileCard } from "@/components/ProfileCard";
import { SentimentTrend } from "@/components/SentimentTrend";
import { StateBadge } from "@/components/StateBadge";
import { StatePanel } from "@/components/StatePanel";
import { StaleBadge } from "@/components/StaleBadge";
import { fetchAssetDetailServer } from "@/lib/queries/asset-detail";

type Props = { params: Promise<{ symbol: string }> };

export const dynamic = "force-dynamic";

export default async function AssetDetailPage({ params }: Props) {
  const { symbol } = await params;
  const detail = await fetchAssetDetailServer(symbol);
  const sym = detail.symbol;
  const anyStale = Boolean(
    detail.bars?.provenance.stale ||
      detail.state?.provenance.stale ||
      detail.profile?.provenance.stale ||
      detail.sentiment?.provenance.stale ||
      detail.insight?.provenance.stale,
  );

  return (
    <AppShell mainClassName="mx-auto w-full max-w-6xl flex-1 px-4 py-6">
      <div className="sticky top-0 z-10 -mx-4 mb-6 border-b border-border bg-background/95 px-4 py-3 backdrop-blur">
        <Link
          href="/"
          className="text-xs text-muted hover:text-foreground focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
        >
          ← Dashboard
        </Link>
        <div className="mt-2 flex flex-wrap items-center gap-3">
          <h1 className="font-mono text-xl font-semibold tracking-tight">{sym}</h1>
          <StateBadge regime={detail.state?.regime} />
          <StaleBadge stale={anyStale} />
          {detail.profile?.identity.display_name ? (
            <span className="text-xs text-muted">{detail.profile.identity.display_name}</span>
          ) : null}
        </div>
        <p className="mt-1 text-[10px] text-muted">
          Refetch on navigation · cadences: state/metrics ~15m · sentiment per{" "}
          <code className="font-mono">SENTIMENT_INTERVAL_MINUTES</code>
        </p>
      </div>

      <div className="flex flex-col gap-6">
        <PriceChart
          bars={detail.bars?.bars ?? []}
          regime={detail.state?.regime}
          stale={detail.bars?.provenance.stale}
        />
        <div className="grid gap-6 lg:grid-cols-2">
          <ProfileCard profile={detail.profile} />
          <CorrelationHeatmap profile={detail.profile} />
        </div>
        <StatePanel state={detail.state} />
        <div className="grid gap-6 lg:grid-cols-2">
          <SentimentTrend sentiment={detail.sentiment} />
          <DriverHeadlines sentiment={detail.sentiment} />
        </div>
        <InsightFeed insight={detail.insight} />
      </div>
    </AppShell>
  );
}
