/**
 * Hand-maintained until `pnpm gen:api` regenerates from OpenAPI.
 * Keep in sync with server `/v1` responses (W9·D2).
 */

export type Provenance = {
  sources: string[];
  generated_at: string;
  model_version: string;
  confidence: number;
  stale: boolean;
};

export type AssetListItem = {
  symbol: string;
  display_name: string;
  asset_class: string;
  mt5_ticker?: string | null;
  base_currency?: string | null;
  quote_currency?: string | null;
  venues: string[];
  is_active: boolean;
};

export type AssetListResponse = {
  items: AssetListItem[];
  next_cursor?: string | null;
  has_more: boolean;
  provenance: Provenance;
};

export type MarketState = {
  schema_id: string;
  symbol: string;
  timeframe: string;
  regime: "trending_up" | "trending_down" | "ranging" | "high_volatility";
  volatility_percentile?: number | null;
  trend_strength?: number | null;
  as_of: string;
  provenance: Provenance;
};

export type NewsListItem = {
  id: number;
  external_id: string;
  symbol?: string | null;
  headline: string;
  source: string;
  impact?: string | null;
  published_at?: string | null;
};

export type NewsListResponse = {
  items: NewsListItem[];
  next_cursor?: string | null;
  has_more: boolean;
  provenance: Provenance;
};

/* —— W11 ops / scoring / admin —— */

export type SourceRow = {
  source_id: string;
  name: string;
  kind: string;
  expected_cadence_seconds: number;
  last_seen_at?: string | null;
  status: string;
  age_seconds?: number | null;
  stale: boolean;
};

export type RegistryResponse = {
  checked_at: string;
  sources: SourceRow[];
};

export type WatchdogAlertRow = {
  source_id: string;
  status: string;
  age_seconds?: number | null;
  message: string;
};

export type WatchdogResponse = {
  checked_at: string;
  ok: boolean;
  stale_count: number;
  alerts: WatchdogAlertRow[];
  sources: SourceRow[];
  rows_marked_stale: Record<string, number>;
};

export type OpsSummaryResponse = {
  as_of: string;
  outbox_unpublished: number;
  outbox_published: number;
  llm_spend_usd_day: number;
  ingestion_lag: { source_id: string; age_seconds?: number | null }[];
  health_hint: string;
};

export type SymbolTfAccuracy = {
  symbol: string;
  timeframe: string;
  model_version?: string | null;
  n: number;
  correct: number;
  accuracy?: number | null;
};

export type WeeklyReportItem = {
  id: number;
  week_start: string;
  week_end: string;
  n_scored: number;
  n_correct: number;
  accuracy?: number | null;
  by_symbol_tf: SymbolTfAccuracy[];
  scoring_model?: string | null;
  email_sent_at?: string | null;
  created_at: string;
};

export type WeeklyScoringResponse = {
  items: WeeklyReportItem[];
};

export type ApiKeyPublic = {
  id: number;
  name: string;
  service_name: string;
  role: string;
  is_active: boolean;
  created_at: string;
};

export type ApiKeyListResponse = {
  items: ApiKeyPublic[];
};

export type MintKeyResponse = {
  key: ApiKeyPublic;
  plaintext: string;
};
