/** Shared Market Pulse focus + desk mix types. */

export type PulseFocus =
  | "assets"
  | "impact"
  | "trending_up"
  | "trending_down"
  | "ranging"
  | "high_volatility";

export type PulseRegimeKey =
  | "trending_up"
  | "trending_down"
  | "ranging"
  | "high_volatility";

export type PulseRegimeMix = Record<PulseRegimeKey, number>;

export const PULSE_REGIME_ORDER: PulseRegimeKey[] = [
  "trending_up",
  "trending_down",
  "ranging",
  "high_volatility",
];

export const PULSE_FOCUS_COPY: Record<PulseFocus, string> = {
  assets:
    "Universe breadth under watch — every active instrument staged on this research desk.",
  impact:
    "High-impact headline pressure in the current cut — severity emphasised over noise.",
  trending_up: "Bullish regime weight across the board — upward structure in focus.",
  trending_down: "Bearish regime weight — downside structure elevated on the desk.",
  ranging: "Range-bound share — mean-reversion and quiet structure dominate.",
  high_volatility: "High-vol share — dispersion and risk premium elevated.",
};

export function emptyRegimeMix(): PulseRegimeMix {
  return {
    trending_up: 0,
    trending_down: 0,
    ranging: 0,
    high_volatility: 0,
  };
}

export function mixFromRegimes(
  regimes: Array<string | null | undefined>,
): PulseRegimeMix {
  const mix = emptyRegimeMix();
  for (const r of regimes) {
    if (r === "trending_up") mix.trending_up += 1;
    else if (r === "trending_down") mix.trending_down += 1;
    else if (r === "ranging") mix.ranging += 1;
    else if (r === "high_volatility") mix.high_volatility += 1;
  }
  return mix;
}

export function isPulseRegimeKey(value: string): value is PulseRegimeKey {
  return (PULSE_REGIME_ORDER as readonly string[]).includes(value);
}
