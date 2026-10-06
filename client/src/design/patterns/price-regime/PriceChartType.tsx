"use client";

import {
  DS_CHART_LABEL,
  DS_CHART_TYPES,
  type DsChartType,
} from "@/design/patterns/charts/chart-types";
import { cn } from "@/lib/utils";

type PriceChartTypeProps = {
  value: DsChartType;
  onChange: (type: DsChartType) => void;
};

/** Asset chart type — typography tabs matching timeframe. */
export function PriceChartType({ value, onChange }: PriceChartTypeProps) {
  return (
    <div className="ds-price-tf" role="radiogroup" aria-label="Chart type">
      {DS_CHART_TYPES.map((type) => {
        const active = value === type;
        return (
          <button
            key={type}
            type="button"
            role="radio"
            aria-checked={active}
            className={cn("ds-price-tf__tab", active && "is-active")}
            onClick={() => onChange(type)}
          >
            {DS_CHART_LABEL[type]}
          </button>
        );
      })}
    </div>
  );
}
