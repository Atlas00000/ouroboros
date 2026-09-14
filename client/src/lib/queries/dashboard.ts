import { fetchApi } from "@/lib/api/client";
import type { AssetListItem, AssetListResponse, MarketState, Provenance } from "@/lib/api/types";

export type DashboardCard = {
  asset: AssetListItem;
  regime?: string | null;
  volPercentile?: number | null;
  sentimentScore?: number | null;
  stale: boolean;
};

export type DashboardPayload = {
  cards: DashboardCard[];
  listProvenance?: Provenance;
  newsHighImpactCount: number;
};

type MetricsSnippet = {
  realized_vol_percentile_30d?: number | null;
  provenance?: Provenance;
};

type SentimentSnippet = {
  score?: number;
  provenance?: Provenance;
};

async function withKey<T>(path: string, key: string): Promise<T | null> {
  try {
    return await fetchApi<T>(path, { serverApiKey: key });
  } catch {
    return null;
  }
}

/** Enrich universe for Dashboard cards (state + metrics + sentiment). */
export async function fetchDashboardServer(): Promise<DashboardPayload | null> {
  const key = process.env.OUROBOROS_SERVER_API_KEY;
  if (!key) return null;

  const list = await withKey<AssetListResponse>("/v1/assets?limit=50&active_only=true", key);
  if (!list) return null;

  const cards = await Promise.all(
    list.items.map(async (asset) => enrichCard(asset, key)),
  );

  const news = await withKey<{ items: unknown[] }>(
    "/v1/news?limit=20&impact=high",
    key,
  );

  return {
    cards,
    listProvenance: list.provenance,
    newsHighImpactCount: news?.items?.length ?? 0,
  };
}

async function enrichCard(asset: AssetListItem, key: string): Promise<DashboardCard> {
  const sym = encodeURIComponent(asset.symbol);
  const [state, metrics, sentiment] = await Promise.all([
    withKey<MarketState>(`/v1/state?symbol=${sym}&timeframe=H1`, key),
    withKey<MetricsSnippet>(`/v1/metrics?symbol=${sym}&timeframe=H1`, key),
    withKey<SentimentSnippet>(`/v1/sentiment?symbol=${sym}`, key),
  ]);

  const stale = Boolean(
    state?.provenance?.stale ||
      metrics?.provenance?.stale ||
      sentiment?.provenance?.stale,
  );

  return {
    asset,
    regime: state?.regime ?? null,
    volPercentile: metrics?.realized_vol_percentile_30d ?? null,
    sentimentScore: sentiment?.score ?? null,
    stale,
  };
}
