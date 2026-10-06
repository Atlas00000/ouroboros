import { AssetGrid } from "@/components/AssetGrid";
import { DeskHero } from "@/design/patterns/desk-hero";
import { SignalTicker } from "@/design/patterns/news-ticker";
import { ActionRail } from "@/design/shells/ActionRail";
import { AppShell } from "@/design/shells/AppShell";
import { fetchDashboardServer } from "@/lib/queries/dashboard";
import { fetchNewsServer } from "@/lib/queries/server";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const [dashboard, news] = await Promise.all([
    fetchDashboardServer(),
    fetchNewsServer(12),
  ]);

  return (
    <AppShell
      wide
      rail={
        <ActionRail>
          <SignalTicker items={news?.items ?? []} />
        </ActionRail>
      }
    >
      <DeskHero
        cards={dashboard?.cards ?? []}
        newsItems={news?.items ?? []}
        stale={dashboard?.listProvenance?.stale}
        generatedAt={dashboard?.listProvenance?.generated_at}
      />
      <AssetGrid initial={dashboard} />
    </AppShell>
  );
}
