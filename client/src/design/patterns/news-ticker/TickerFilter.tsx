"use client";

import { impactLabel, normalizeImpact, type ImpactLevel } from "@/design/patterns/news-ticker/TickerImpact";
import { cn } from "@/lib/utils";

export type TickerFilterKey = "all" | ImpactLevel;

const FILTERS: { key: TickerFilterKey; label: string }[] = [
  { key: "all", label: "All" },
  { key: "high", label: impactLabel("high") },
  { key: "medium", label: impactLabel("medium") },
  { key: "low", label: impactLabel("low") },
];

type TickerFilterProps = {
  value: TickerFilterKey;
  counts: Record<TickerFilterKey, number>;
  onChange: (key: TickerFilterKey) => void;
};

/** Impact focus tabs — underline signal, not Bootstrap pills. */
export function TickerFilter({ value, counts, onChange }: TickerFilterProps) {
  return (
    <div className="ds-ticker-filter" role="tablist" aria-label="Filter headlines by impact">
      {FILTERS.map((f) => {
        const active = value === f.key;
        return (
          <button
            key={f.key}
            type="button"
            role="tab"
            aria-selected={active}
            className={cn("ds-ticker-filter__tab", active && "is-active")}
            data-level={f.key}
            onClick={() => onChange(f.key)}
          >
            <span className="ds-ticker-filter__label">{f.label}</span>
            <span className="ds-ticker-filter__count">{counts[f.key] ?? 0}</span>
          </button>
        );
      })}
    </div>
  );
}

export function countByImpact(
  impacts: Array<string | null | undefined>,
): Record<TickerFilterKey, number> {
  const counts: Record<TickerFilterKey, number> = {
    all: impacts.length,
    high: 0,
    medium: 0,
    low: 0,
    unknown: 0,
  };
  for (const raw of impacts) {
    const level = normalizeImpact(raw);
    counts[level] += 1;
  }
  return counts;
}
