"use client";

import type { CSSProperties } from "react";

import {
  formatSharePct,
  type FitShareRow,
} from "@/design/patterns/fit/fit-utils";
import type { FitTag } from "@/lib/api/types";

type FitShareRibbonProps = {
  rows: FitShareRow[];
  activeTag: FitTag | null;
  window?: string | null;
  onSelect: (tag: FitTag) => void;
};

/** Proportional share ribbon for the lookback window. */
export function FitShareRibbon({
  rows,
  activeTag,
  window,
  onSelect,
}: FitShareRibbonProps) {
  const hasMass = rows.some((r) => r.share > 0);

  return (
    <div className="ds-fit-share">
      <div className="ds-fit-share__head">
        <span>{window ?? "30d"} share</span>
        <span>dominant tag mass over the window</span>
      </div>
      {hasMass ? (
        <div className="ds-fit-share__ribbon" role="list" aria-label="Fit share ribbon">
          {rows.map((row, i) => {
            if (row.share <= 0) return null;
            const active = row.tag === activeTag;
            return (
              <button
                key={row.tag}
                type="button"
                role="listitem"
                className="ds-fit-share__seg"
                style={
                  {
                    flexGrow: Math.max(row.share, 0.04),
                    ["--ds-fit-cell" as string]: row.color,
                    animationDelay: `${i * 45}ms`,
                  } as CSSProperties
                }
                data-active={active ? "true" : "false"}
                aria-pressed={active}
                aria-label={`${row.label} ${formatSharePct(row.share)}`}
                onClick={() => onSelect(row.tag)}
              >
                <span className="ds-fit-share__seg-label">
                  {row.pct >= 12 ? row.label : ""}
                </span>
              </button>
            );
          })}
        </div>
      ) : (
        <p className="ds-fit-share__empty">No share mass in this window yet.</p>
      )}
    </div>
  );
}
