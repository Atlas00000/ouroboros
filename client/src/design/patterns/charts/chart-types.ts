/** Shared price chart render modes — line (area) is default. */

export const DS_CHART_TYPES = ["line", "candles"] as const;

export type DsChartType = (typeof DS_CHART_TYPES)[number];

export const DS_CHART_DEFAULT: DsChartType = "line";

export const DS_CHART_LABEL: Record<DsChartType, string> = {
  line: "Line",
  candles: "Candles",
};

export function isDsChartType(value: string): value is DsChartType {
  return (DS_CHART_TYPES as readonly string[]).includes(value);
}
