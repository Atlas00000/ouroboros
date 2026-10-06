/** Asset dossier bar timeframes — matches /v1/bars (no M5). */

export const ASSET_BAR_TIMEFRAMES = ["M15", "H1", "H4", "D1"] as const;

export type AssetBarTimeframe = (typeof ASSET_BAR_TIMEFRAMES)[number];

export const ASSET_BAR_DEFAULT: AssetBarTimeframe = "H1";

export const ASSET_BAR_LABEL: Record<AssetBarTimeframe, string> = {
  M15: "15m",
  H1: "1h",
  H4: "4h",
  D1: "1d",
};

export const ASSET_BAR_LOOKBACK_DAYS: Record<AssetBarTimeframe, number> = {
  M15: 21,
  H1: 45,
  H4: 90,
  D1: 180,
};

export function isAssetBarTimeframe(value: string): value is AssetBarTimeframe {
  return (ASSET_BAR_TIMEFRAMES as readonly string[]).includes(value);
}

export type AssetBarPoint = {
  ts: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number | null;
};
