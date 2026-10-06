"use client";

import { NumberTick } from "@/design/motion/NumberTick";

type RegimeNowcastMetricsProps = {
  volPct: number | null | undefined;
  trendEr: number | null | undefined;
  confidence: number;
  asOf: string;
};

export function RegimeNowcastMetrics({
  volPct,
  trendEr,
  confidence,
  asOf,
}: RegimeNowcastMetricsProps) {
  return (
    <dl className="ds-reg-now-metrics">
      <div>
        <dt>Vol pct</dt>
        <dd>
          <NumberTick value={volPct != null ? Math.round(volPct) : null} />
        </dd>
      </div>
      <div>
        <dt>Trend ER</dt>
        <dd>
          <NumberTick value={trendEr != null ? trendEr.toFixed(2) : null} />
        </dd>
      </div>
      <div>
        <dt>Confidence</dt>
        <dd>
          <NumberTick value={confidence.toFixed(2)} />
        </dd>
      </div>
      <div>
        <dt>As of</dt>
        <dd className="ds-reg-now-metrics__asof">{asOf.slice(0, 16).replace("T", " ")}</dd>
      </div>
    </dl>
  );
}
