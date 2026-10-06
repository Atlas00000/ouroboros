import { fetchApi } from "@/lib/api/client";
import type { AssetListItem, AssetListResponse, MarketState, Provenance } from "@/lib/api/types";

export type DashboardCard = {
  asset: AssetListItem;
  regime?: string | null;
  volPercentile?: number | null;
  sentimentScore?: number | null;
  /** M15 close series for universe mini-charts (newest last). */
  closes?: number[];
  lastClose?: number | null;
  /** Percent change across the loaded window. */
  changePct?: number | null;
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

const SPARK_MAX_POINTS = 48;

export function seriesFromBars(
  bars:
    | { open?: number; high?: number; low?: number; close: number }[]
    | undefined,
): {
  closes: number[];
  bars: { open: number; high: number; low: number; close: number }[];
  lastClose: number | null;
  changePct: number | null;
} {
  const slice = (bars ?? []).slice(-SPARK_MAX_POINTS);
  const closes = slice.map((b) => b.close);
  const ohlc = slice.map((b) => {
    const close = b.close;
    const open = typeof b.open === "number" ? b.open : close;
    const high = typeof b.high === "number" ? b.high : Math.max(open, close);
    const low = typeof b.low === "number" ? b.low : Math.min(open, close);
    return { open, high, low, close };
  });
  if (closes.length < 2) {
    return {
      closes,
      bars: ohlc,
      lastClose: closes[0] ?? null,
      changePct: null,
    };
  }
  const first = closes[0];
  const last = closes[closes.length - 1];
  const changePct = first === 0 ? null : ((last - first) / first) * 100;
  return { closes, bars: ohlc, lastClose: last, changePct };
}

async function withKey<T>(path: string, key: string): Promise<T | null> {
  try {
    return await fetchApi<T>(path, { serverApiKey: key });
  } catch {
    return null;
  }
}

/** Cap parallel symbol enrichments so we don't exhaust the API DB pool. */
const ENRICH_CONCURRENCY = 4;

export async function mapPool<T, R>(
  items: T[],
  concurrency: number,
  fn: (item: T) => Promise<R>,
): Promise<R[]> {
  if (items.length === 0) return [];
  const results = new Array<R>(items.length);
  let next = 0;
  const workers = Array.from(
    { length: Math.min(concurrency, items.length) },
    async () => {
      while (true) {
        const i = next++;
        if (i >= items.length) return;
        results[i] = await fn(items[i]);
      }
    },
  );
  await Promise.all(workers);
  return results;
}

/**
 * Home SSR payload — asset list + high-impact news only.
 * Per-symbol state/metrics/sentiment enrich on the client (see AssetGrid)
 * so the loading shell is not blocked by N×3 API calls / DB pool pressure.
 */
export async function fetchDashboardServer(): Promise<DashboardPayload | null> {
  const key = process.env.OUROBOROS_SERVER_API_KEY;
  if (!key) return null;

  const [list, news] = await Promise.all([
    withKey<AssetListResponse>("/v1/assets?limit=50&active_only=true", key),
    withKey<{ items: unknown[] }>("/v1/news?limit=20&impact=high", key),
  ]);
  if (!list) return null;

  const cards: DashboardCard[] = list.items.map((asset) => ({
    asset,
    regime: null,
    volPercentile: null,
    sentimentScore: null,
    closes: [],
    lastClose: null,
    changePct: null,
    stale: Boolean(list.provenance?.stale),
  }));

  return {
    cards,
    listProvenance: list.provenance,
    newsHighImpactCount: news?.items?.length ?? 0,
  };
}

/** Optional server-side enrich (tests / non-Clerk shells). */
export async function enrichDashboardCards(
  cards: DashboardCard[],
  key: string,
): Promise<DashboardCard[]> {
  return mapPool(cards, ENRICH_CONCURRENCY, (card) => enrichCard(card.asset, key));
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
    // M15 closes load via /api/universe-spark (Recharts) so SSR home stays lean.
    closes: [],
    lastClose: null,
    changePct: null,
    stale,
  };
}
