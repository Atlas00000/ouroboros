"use client";

import {
  UNIVERSE_CHART_LABEL,
  UNIVERSE_CHART_TYPES,
  type UniverseChartType,
} from "@/design/patterns/universe/spark";
import { cn } from "@/lib/utils";

type UniverseChartTypeProps = {
  value: UniverseChartType;
  onChange: (type: UniverseChartType) => void;
};

/** Chart type selector — typography tabs matching timeframe control. */
export function UniverseChartTypeControl({ value, onChange }: UniverseChartTypeProps) {
  return (
    <div
      className="ds-universe-timeframe"
      role="radiogroup"
      aria-label="Chart type"
    >
      <span className="ds-universe-timeframe__eyebrow">Chart</span>
      <div className="ds-universe-timeframe__tabs">
        {UNIVERSE_CHART_TYPES.map((type) => {
          const active = value === type;
          return (
            <button
              key={type}
              type="button"
              role="radio"
              aria-checked={active}
              className={cn("ds-universe-timeframe__tab", active && "is-active")}
              onClick={() => onChange(type)}
            >
              {UNIVERSE_CHART_LABEL[type]}
            </button>
          );
        })}
      </div>
    </div>
  );
}
