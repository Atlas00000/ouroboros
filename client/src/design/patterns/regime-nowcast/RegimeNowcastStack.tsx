"use client";

import type { CSSProperties } from "react";

import {
  formatProbPct,
  type NowcastProb,
} from "@/design/patterns/regime-nowcast/nowcast-utils";

type RegimeNowcastStackProps = {
  rows: NowcastProb[];
  activeRegime: string | null;
  onSelect: (regime: string) => void;
};

export function RegimeNowcastStack({
  rows,
  activeRegime,
  onSelect,
}: RegimeNowcastStackProps) {
  return (
    <div className="ds-reg-now-stack" role="list" aria-label="Probability stack">
      <div className="ds-reg-now-stack__ribbon">
        {rows.map((row, i) => {
          const active = row.regime === activeRegime;
          return (
            <button
              key={row.regime}
              type="button"
              role="listitem"
              className="ds-reg-now-stack__seg"
              style={
                {
                  flexGrow: Math.max(row.probability, 0.02),
                  ["--ds-reg-tone" as string]: row.color,
                  animationDelay: `${i * 50}ms`,
                } as CSSProperties
              }
              data-active={active ? "true" : "false"}
              aria-pressed={active}
              aria-label={`${row.label} ${formatProbPct(row.pct)}`}
              onClick={() => onSelect(row.regime)}
            >
              <span className="ds-reg-now-stack__seg-label">
                {row.pct >= 14 ? row.label : ""}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
