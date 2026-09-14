import { AppShell } from "@/components/AppShell";
import { AssetGrid } from "@/components/AssetGrid";
import { MarketSummaryStrip } from "@/components/MarketSummaryStrip";
import { NewsTicker } from "@/components/NewsTicker";
import { fetchDashboardServer } from "@/lib/queries/dashboard";
import { fetchNewsServer } from "@/lib/queries/server";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const [dashboard, news] = await Promise.all([fetchDashboardServer(), fetchNewsServer(8)]);

  return (
    <AppShell>
      <div>
        <h1 className="text-lg font-semibold tracking-tight text-foreground">Ouroboros</h1>
        <p className="mt-1 text-sm text-muted">
          Living asset profiles, regimes, and news context for sibling platforms.
        </p>
      </div>
      <MarketSummaryStrip
        assetCount={dashboard?.cards.length ?? 0}
        highImpactCount={dashboard?.newsHighImpactCount}
        stale={dashboard?.listProvenance?.stale}
        generatedAt={dashboard?.listProvenance?.generated_at}
      />
      <div className="grid gap-6 lg:grid-cols-[1fr_minmax(0,280px)]">
        <AssetGrid initial={dashboard} />
        <aside aria-label="High-impact news">
          <NewsTicker items={news?.items ?? []} />
        </aside>
      </div>
    </AppShell>
  );
}
