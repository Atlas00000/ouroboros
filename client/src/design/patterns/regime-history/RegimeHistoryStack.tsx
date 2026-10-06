"use client";

import type { CSSProperties } from "react";

import { formatSharePct, type RegimeShareRow } from "@/design/patterns/regime-history/regime-history-utils";

type RegimeHistoryStackProps = {
  rows: RegimeShareRow[];
  activeRegime: string | null;
  onSelect: (regime: string) => void;
};

/** Proportional history ribbon — click a segment to focus. */
export function RegimeHistoryStack({
  rows,
  activeRegime,
  onSelect,
}: RegimeHistoryStackProps) {
  return (
    <div className="ds-reg-hist-stack" role="list" aria-label="History share stack">
      <div className="ds-reg-hist-stack__ribbon">
        {rows.map((row, i) => {
          const active = row.regime === activeRegime;
          return (
            <button
              key={row.regime}
              type="button"
              role="listitem"
              className="ds-reg-hist-stack__seg"
              style={
                {
                  flexGrow: Math.max(row.share, 0.02),
                  ["--ds-reg-tone" as string]: row.color,
                  animationDelay: `${i * 50}ms`,
                } as CSSProperties
              }
              data-active={active ? "true" : "false"}
              aria-pressed={active}
              aria-label={`${row.label} ${formatSharePct(row.pct)}`}
              onClick={() => onSelect(row.regime)}
            >
              <span className="ds-reg-hist-stack__seg-label">
                {row.pct >= 12 ? row.label : ""}
              </span>
            </button>
          );
        })}
      </div>
      <div className="ds-reg-hist-stack__legend" aria-hidden>
        <span>0%</span>
        <span>Share of confirmed history</span>
        <span>100%</span>
      </div>
    </div>
  );
}
