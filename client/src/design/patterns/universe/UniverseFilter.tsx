"use client";

import { REGIME_LABEL } from "@/design/map/backend-visual";
import { cn } from "@/lib/utils";

export type UniverseFilterKey = "all" | "trending_up" | "trending_down" | "ranging" | "high_volatility";

const FILTERS: { key: UniverseFilterKey; label: string }[] = [
  { key: "all", label: "All" },
  { key: "trending_up", label: REGIME_LABEL.trending_up },
  { key: "trending_down", label: REGIME_LABEL.trending_down },
  { key: "ranging", label: REGIME_LABEL.ranging },
  { key: "high_volatility", label: REGIME_LABEL.high_volatility },
];

type UniverseFilterProps = {
  value: UniverseFilterKey;
  counts: Record<UniverseFilterKey, number>;
  onChange: (key: UniverseFilterKey) => void;
};

/** Regime focus rail — typography tabs, not pill clusters. */
export function UniverseFilter({ value, counts, onChange }: UniverseFilterProps) {
  return (
    <div className="ds-universe-filter" role="tablist" aria-label="Filter universe by regime">
      {FILTERS.map((f) => {
        const active = value === f.key;
        const count = counts[f.key] ?? 0;
        return (
          <button
            key={f.key}
            type="button"
            role="tab"
            aria-selected={active}
            className={cn("ds-universe-filter__tab", active && "is-active")}
            data-regime={f.key}
            onClick={() => onChange(f.key)}
          >
            <span className="ds-universe-filter__label">{f.label}</span>
            <span className="ds-universe-filter__count">{count}</span>
          </button>
        );
      })}
    </div>
  );
}
