"use client";

import {
  ASSET_BAR_LABEL,
  ASSET_BAR_TIMEFRAMES,
  type AssetBarTimeframe,
} from "@/design/patterns/price-regime/timeframes";
import { cn } from "@/lib/utils";

type PriceTimeframeProps = {
  value: AssetBarTimeframe;
  onChange: (tf: AssetBarTimeframe) => void;
};

/** Asset chart timeframe — typography tabs. */
export function PriceTimeframe({ value, onChange }: PriceTimeframeProps) {
  return (
    <div className="ds-price-tf" role="radiogroup" aria-label="Price timeframe">
      {ASSET_BAR_TIMEFRAMES.map((tf) => {
        const active = value === tf;
        return (
          <button
            key={tf}
            type="button"
            role="radio"
            aria-checked={active}
            className={cn("ds-price-tf__tab", active && "is-active")}
            onClick={() => onChange(tf)}
          >
            {ASSET_BAR_LABEL[tf]}
          </button>
        );
      })}
    </div>
  );
}
