"use client";

import Link from "next/link";
import { useAuth } from "@clerk/nextjs";
import { useQuery } from "@tanstack/react-query";

import { SentimentGauge } from "@/components/SentimentGauge";
import { Sparkline } from "@/components/Sparkline";
import { StateBadge } from "@/components/StateBadge";
import { StaleBadge } from "@/components/StaleBadge";
import { EmptyState, ErrorState, LoadingState } from "@/components/ui/PageState";
import { VolPercentile } from "@/components/VolPercentile";
import { fetchApi } from "@/lib/api/client";
import type { AssetListResponse, MarketState } from "@/lib/api/types";
import type { DashboardCard, DashboardPayload } from "@/lib/queries/dashboard";

const clerkEnabled = Boolean(process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY);

function CardView({ card }: { card: DashboardCard }) {
  const { asset, regime, volPercentile, sentimentScore, stale } = card;
  return (
    <Link
      href={`/assets/${asset.symbol}`}
      className="block rounded-md border border-border bg-card px-3 py-3 transition hover:border-accent/40"
    >
      <div className="flex items-start justify-between gap-2">
        <div>
          <div className="flex items-center gap-2">
            <span className="font-mono text-sm font-semibold tracking-tight">{asset.symbol}</span>
            <StaleBadge stale={stale} />
          </div>
          <div className="text-[11px] text-muted">{asset.display_name}</div>
        </div>
        <StateBadge regime={regime} />
      </div>
      <Sparkline className="mt-3 h-6 w-full" />
      <div className="mt-2 flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 text-[11px] text-muted">
          <span>vol</span>
          <VolPercentile value={volPercentile} />
        </div>
        <SentimentGauge score={sentimentScore} />
      </div>
    </Link>
  );
}

function GridShell({
  cards,
  listStale,
  loading,
  error,
  generatedAt,
}: {
  cards: DashboardCard[];
  listStale?: boolean;
  loading?: boolean;
  error?: string | null;
  generatedAt?: string;
}) {
  if (loading) {
    return <LoadingState>Loading assets…</LoadingState>;
  }
  if (error) {
    return <ErrorState title="Could not load universe">{error}</ErrorState>;
  }
  if (!cards.length) {
    return (
      <EmptyState title="No assets yet">
        Start Docker + API and set{" "}
        <code className="font-mono text-foreground">OUROBOROS_SERVER_API_KEY</code> for local SSR,
        or sign in with Clerk.
      </EmptyState>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-2">
        <h2 className="text-sm font-medium text-foreground">Universe</h2>
        <StaleBadge stale={listStale} />
        {generatedAt ? (
          <span className="text-[10px] text-muted">as of {generatedAt}</span>
        ) : null}
      </div>
      <ul className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
        {cards.map((c) => (
          <li key={c.asset.symbol}>
            <CardView card={c} />
          </li>
        ))}
      </ul>
    </div>
  );
}

async function enrichClient(
  list: AssetListResponse,
  token: string | null,
): Promise<DashboardCard[]> {
  return Promise.all(
    list.items.map(async (asset) => {
      const sym = encodeURIComponent(asset.symbol);
      const [state, metrics, sentiment] = await Promise.all([
        fetchApi<MarketState>(`/v1/state?symbol=${sym}&timeframe=H1`, { token }).catch(() => null),
        fetchApi<{ realized_vol_percentile_30d?: number; provenance?: { stale?: boolean } }>(
          `/v1/metrics?symbol=${sym}&timeframe=H1`,
          { token },
        ).catch(() => null),
        fetchApi<{ score?: number; provenance?: { stale?: boolean } }>(
          `/v1/sentiment?symbol=${sym}`,
          { token },
        ).catch(() => null),
      ]);
      return {
        asset,
        regime: state?.regime ?? null,
        volPercentile: metrics?.realized_vol_percentile_30d ?? null,
        sentimentScore: sentiment?.score ?? null,
        stale: Boolean(
          state?.provenance?.stale || metrics?.provenance?.stale || sentiment?.provenance?.stale,
        ),
      };
    }),
  );
}

function AssetGridLive({ initial }: { initial: DashboardPayload | null }) {
  const { getToken, isLoaded } = useAuth();
  const q = useQuery({
    queryKey: ["dashboard-cards"],
    enabled: isLoaded,
    initialData: initial ?? undefined,
    queryFn: async () => {
      const token = await getToken();
      const list = await fetchApi<AssetListResponse>("/v1/assets?limit=50&active_only=true", {
        token,
      });
      const cards = await enrichClient(list, token);
      return {
        cards,
        listProvenance: list.provenance,
        newsHighImpactCount: initial?.newsHighImpactCount ?? 0,
      } satisfies DashboardPayload;
    },
  });

  return (
    <GridShell
      cards={q.data?.cards ?? []}
      listStale={q.data?.listProvenance?.stale}
      generatedAt={q.data?.listProvenance?.generated_at}
      loading={q.isLoading && !initial}
      error={q.isError ? "Failed to load assets" : null}
    />
  );
}

export function AssetGrid({ initial }: { initial: DashboardPayload | null }) {
  if (clerkEnabled) {
    return <AssetGridLive initial={initial} />;
  }
  return (
    <GridShell
      cards={initial?.cards ?? []}
      listStale={initial?.listProvenance?.stale}
      generatedAt={initial?.listProvenance?.generated_at}
      error={
        initial
          ? null
          : "Configure Clerk or OUROBOROS_SERVER_API_KEY to load the universe."
      }
    />
  );
}
