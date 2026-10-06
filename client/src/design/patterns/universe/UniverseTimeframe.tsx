"use client";

import {
  UNIVERSE_SPARK_LABEL,
  UNIVERSE_SPARK_TIMEFRAMES,
  type UniverseSparkTimeframe,
} from "@/design/patterns/universe/spark";
import { cn } from "@/lib/utils";

type UniverseTimeframeProps = {
  value: UniverseSparkTimeframe;
  onChange: (tf: UniverseSparkTimeframe) => void;
};

/** Chart timeframe selector — typography tabs, not a Bootstrap dropdown. */
export function UniverseTimeframe({ value, onChange }: UniverseTimeframeProps) {
  return (
    <div
      className="ds-universe-timeframe"
      role="radiogroup"
      aria-label="Chart timeframe"
    >
      <span className="ds-universe-timeframe__eyebrow">Timeframe</span>
      <div className="ds-universe-timeframe__tabs">
        {UNIVERSE_SPARK_TIMEFRAMES.map((tf) => {
          const active = value === tf;
          return (
            <button
              key={tf}
              type="button"
              role="radio"
              aria-checked={active}
              className={cn("ds-universe-timeframe__tab", active && "is-active")}
              onClick={() => onChange(tf)}
            >
              {UNIVERSE_SPARK_LABEL[tf]}
            </button>
          );
        })}
      </div>
    </div>
  );
}
