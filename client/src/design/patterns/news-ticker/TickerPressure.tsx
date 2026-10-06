"use client";

import type { CSSProperties } from "react";

import {
  impactLabel,
  impactToneVar,
  type ImpactLevel,
} from "@/design/patterns/news-ticker/TickerImpact";
import type { TickerFilterKey } from "@/design/patterns/news-ticker/TickerFilter";
import { cn } from "@/lib/utils";

type TickerPressureProps = {
  value: TickerFilterKey;
  counts: Record<TickerFilterKey, number>;
  onChange: (key: TickerFilterKey) => void;
};

const BANDS: { key: TickerFilterKey; level?: ImpactLevel }[] = [
  { key: "all" },
  { key: "high", level: "high" },
  { key: "medium", level: "medium" },
  { key: "low", level: "low" },
];

/** Soft impact cut — inline text, not brick tabs. */
export function TickerPressure({ value, counts, onChange }: TickerPressureProps) {
  return (
    <div
      className="ds-ticker-pressure"
      role="radiogroup"
      aria-label="Impact pressure"
    >
      {BANDS.map(({ key, level }, i) => {
        const active = value === key;
        const label = key === "all" ? "All" : impactLabel(level!);
        return (
          <span key={key} className="ds-ticker-pressure__slot">
            {i > 0 ? <span className="ds-ticker-pressure__sep" aria-hidden>·</span> : null}
            <button
              type="button"
              role="radio"
              aria-checked={active}
              className={cn("ds-ticker-pressure__chip", active && "is-active")}
              style={
                level
                  ? ({ ["--ds-pressure-tone" as string]: impactToneVar(level) } as CSSProperties)
                  : undefined
              }
              onClick={() => onChange(key)}
            >
              {label}
              <span className="ds-ticker-pressure__count">{counts[key] ?? 0}</span>
            </button>
          </span>
        );
      })}
    </div>
  );
}
