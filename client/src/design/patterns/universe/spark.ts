/** Universe spark timeframes — matches /v1/bars (no M5 on API). */

import {
  DS_CHART_DEFAULT,
  DS_CHART_LABEL,
  DS_CHART_TYPES,
  isDsChartType,
  type DsChartType,
} from "@/design/patterns/charts/chart-types";

export const UNIVERSE_SPARK_TIMEFRAMES = ["M1", "M15", "H1", "H4", "D1"] as const;

export type UniverseSparkTimeframe = (typeof UNIVERSE_SPARK_TIMEFRAMES)[number];

export const UNIVERSE_SPARK_DEFAULT: UniverseSparkTimeframe = "M15";

export const UNIVERSE_SPARK_LABEL: Record<UniverseSparkTimeframe, string> = {
  M1: "1m",
  M15: "15m",
  H1: "1h",
  H4: "4h",
  D1: "1d",
};

/** Aliases of shared DS_CHART_* for Universe consumers. */
export const UNIVERSE_CHART_TYPES = DS_CHART_TYPES;
export type UniverseChartType = DsChartType;
export const UNIVERSE_CHART_DEFAULT = DS_CHART_DEFAULT;
export const UNIVERSE_CHART_LABEL = DS_CHART_LABEL;
export const isUniverseChartType = isDsChartType;

/** Lookback long enough for a stale local MT5 cut (~mid/late Sept). */
export const UNIVERSE_SPARK_LOOKBACK_DAYS: Record<UniverseSparkTimeframe, number> = {
  M1: 21,
  M15: 21,
  H1: 45,
  H4: 90,
  D1: 180,
};

export function isUniverseSparkTimeframe(value: string): value is UniverseSparkTimeframe {
  return (UNIVERSE_SPARK_TIMEFRAMES as readonly string[]).includes(value);
}

export type UniverseSparkOhlc = {
  open: number;
  high: number;
  low: number;
  close: number;
};

export type UniverseSparkSeries = {
  symbol: string;
  timeframe: string;
  closes: number[];
  bars: UniverseSparkOhlc[];
  lastClose: number | null;
  changePct: number | null;
};
