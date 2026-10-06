"use client";

import type { CSSProperties } from "react";

import { NumberTick } from "@/design/motion/NumberTick";
import {
  formatSharePct,
  type RegimeShareRow,
} from "@/design/patterns/regime-history/regime-history-utils";

type RegimeHistoryLanesProps = {
  rows: RegimeShareRow[];
  activeRegime: string | null;
  onSelect: (regime: string) => void;
};

export function RegimeHistoryLanes({
  rows,
  activeRegime,
  onSelect,
}: RegimeHistoryLanesProps) {
  return (
    <div className="ds-reg-hist-lanes" role="list" aria-label="Ranked regime shares">
      {rows.map((row, i) => {
        const active = row.regime === activeRegime;
        return (
          <button
            key={row.regime}
            type="button"
            role="listitem"
            className="ds-reg-hist-lane"
            style={
              {
                ["--ds-reg-tone" as string]: row.color,
                animationDelay: `${i * 45}ms`,
              } as CSSProperties
            }
            data-active={active ? "true" : "false"}
            aria-pressed={active}
            onClick={() => onSelect(row.regime)}
          >
            <span className="ds-reg-hist-lane__label">{row.label}</span>
            <span className="ds-reg-hist-lane__track" aria-hidden>
              <span
                className="ds-reg-hist-lane__fill"
                style={{ width: `${Math.min(100, row.pct)}%` }}
              />
            </span>
            <span className="ds-reg-hist-lane__pct">
              <NumberTick value={formatSharePct(row.pct)} />
            </span>
          </button>
        );
      })}
    </div>
  );
}
