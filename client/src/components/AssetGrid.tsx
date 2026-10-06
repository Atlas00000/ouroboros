"use client";

import { useAuth } from "@clerk/nextjs";
import { useQuery } from "@tanstack/react-query";

import { Universe } from "@/design/patterns/universe";
import { fetchApi } from "@/lib/api/client";
import type { AssetListResponse, MarketState } from "@/lib/api/types";
import type { DashboardCard, DashboardPayload } from "@/lib/queries/dashboard";
import { mapPool } from "@/lib/queries/dashboard";
const clerkEnabled = Boolean(process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY);

const ENRICH_CONCURRENCY = 4;

async function enrichClient(
  list: AssetListResponse,
  token: string | null,
): Promise<DashboardCard[]> {
  return mapPool(list.items, ENRICH_CONCURRENCY, async (asset) => {
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
      closes: [],
      lastClose: null,
      changePct: null,
      stale: Boolean(
        state?.provenance?.stale || metrics?.provenance?.stale || sentiment?.provenance?.stale,
      ),
    };
  });
}

function AssetGridLive({ initial }: { initial: DashboardPayload | null }) {
  const { getToken, isLoaded } = useAuth();
  const q = useQuery({
    queryKey: ["dashboard-cards"],
    enabled: isLoaded,
    // Show symbols immediately from SSR; enrich in the background.
    initialData: initial ?? undefined,
    refetchOnMount: "always",
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
    <Universe
      cards={q.data?.cards ?? []}
      listStale={q.data?.listProvenance?.stale}
      generatedAt={q.data?.listProvenance?.generated_at}
      loading={q.isLoading && !initial}
      error={q.isError ? "Failed to load assets" : null}
    />
  );
}

/** Data shell for Home Universe — presentation lives in `design/patterns/universe`. */
export function AssetGrid({ initial }: { initial: DashboardPayload | null }) {
  if (clerkEnabled) {
    return <AssetGridLive initial={initial} />;
  }
  return (
    <Universe
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
