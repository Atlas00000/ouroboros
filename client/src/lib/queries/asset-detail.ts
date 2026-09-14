import { fetchApi } from "@/lib/api/client";
import type { Provenance } from "@/lib/api/types";

export type BarPoint = {
  ts: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number | null;
};

export type BarsResponse = {
  symbol: string;
  timeframe: string;
  bars: BarPoint[];
  provenance: Provenance;
};

export type AssetProfile = {
  schema_id: string;
  profile_version: number;
  identity: {
    symbol: string;
    display_name: string;
    asset_class: string;
    venues: string[];
    mt5_ticker?: string | null;
    base_currency?: string | null;
    quote_currency?: string | null;
  };
  volatility?: {
    atr_percentile_30d?: number | null;
    realized_vol_percentile_30d?: number | null;
    typical_daily_range?: number | null;
  };
  correlations: { symbol: string; coefficient: number; window_days: number }[];
  regime_distribution?: { regime: string; share: number }[];
  as_of: string;
  provenance: Provenance;
  disclaimer?: { text: string };
};

export type MarketState = {
  symbol: string;
  timeframe: string;
  regime: string;
  regime_probabilities: { regime: string; probability: number }[];
  volatility_percentile?: number | null;
  trend_strength?: number | null;
  as_of: string;
  provenance: Provenance;
};

export type SentimentSnapshot = {
  symbol: string;
  score: number;
  item_count: number;
  window_hours: number;
  top_drivers: {
    title: string;
    url?: string | null;
    published_at?: string | null;
    contribution?: number | null;
    source?: string | null;
  }[];
  as_of: string;
  provenance: Provenance;
};

export type Insight = {
  type: string;
  symbol?: string | null;
  title: string;
  body: string;
  tags: string[];
  related_refs: string[];
  as_of: string;
  provenance: Provenance;
  disclaimer: { text: string };
};

export type AssetDetailPayload = {
  symbol: string;
  bars: BarsResponse | null;
  state: MarketState | null;
  profile: AssetProfile | null;
  sentiment: SentimentSnapshot | null;
  insight: Insight | null;
};

async function optional<T>(path: string, key: string): Promise<T | null> {
  try {
    return await fetchApi<T>(path, { serverApiKey: key });
  } catch {
    return null;
  }
}

export async function fetchAssetDetailServer(symbol: string): Promise<AssetDetailPayload> {
  const sym = symbol.toUpperCase();
  const key = process.env.OUROBOROS_SERVER_API_KEY;
  if (!key) {
    return { symbol: sym, bars: null, state: null, profile: null, sentiment: null, insight: null };
  }
  const q = encodeURIComponent(sym);
  const [bars, state, profile, sentiment, insight] = await Promise.all([
    optional<BarsResponse>(`/v1/bars?symbol=${q}&timeframe=H1&lookback_days=45`, key),
    optional<MarketState>(`/v1/state?symbol=${q}&timeframe=H1`, key),
    optional<AssetProfile>(`/v1/assets/${q}/profile`, key),
    optional<SentimentSnapshot>(`/v1/sentiment?symbol=${q}`, key),
    optional<Insight>(`/v1/insights?symbol=${q}`, key),
  ]);
  return { symbol: sym, bars, state, profile, sentiment, insight };
}
