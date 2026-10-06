"use client";

import type { CSSProperties } from "react";

import { NumberTick } from "@/design/motion/NumberTick";
import {
  formatSharePct,
  type RegimeShareRow,
} from "@/design/patterns/regime-history/regime-history-utils";

const R = 36;
const C = 2 * Math.PI * R;

type RegimeHistoryDialProps = {
  rows: RegimeShareRow[];
  active: RegimeShareRow | null;
  onSelect: (regime: string) => void;
};

/** Arc dial for the focused history share + satellite regime chips. */
export function RegimeHistoryDial({ rows, active, onSelect }: RegimeHistoryDialProps) {
  const pct = active?.pct ?? 0;
  const offset = C * (1 - Math.max(0, Math.min(100, pct)) / 100);

  return (
    <div className="ds-reg-hist-dial">
      <div
        className="ds-reg-hist-dial__ring"
        style={{ ["--ds-reg-tone" as string]: active?.color ?? "var(--ds-signal)" } as CSSProperties}
      >
        <svg className="ds-reg-hist-dial__svg" viewBox="0 0 88 88" aria-hidden>
          <circle className="ds-reg-hist-dial__track" cx="44" cy="44" r={R} />
          <circle
            className="ds-reg-hist-dial__arc"
            cx="44"
            cy="44"
            r={R}
            style={
              {
                strokeDasharray: C,
                strokeDashoffset: offset,
                ["--ds-reg-dial-circ" as string]: String(C),
                ["--ds-reg-dial-offset" as string]: String(offset),
              } as CSSProperties
            }
          />
        </svg>
        <div className="ds-reg-hist-dial__core">
          <p className="ds-reg-hist-dial__pct">
            <NumberTick value={active ? formatSharePct(pct) : null} />
          </p>
          <p className="ds-reg-hist-dial__name">{active?.label ?? "—"}</p>
        </div>
      </div>
      <div className="ds-reg-hist-dial__sats" role="list" aria-label="Regime chips">
        {rows.map((row) => {
          const on = row.regime === active?.regime;
          return (
            <button
              key={row.regime}
              type="button"
              role="listitem"
              className="ds-reg-hist-sat"
              style={{ ["--ds-reg-tone" as string]: row.color } as CSSProperties}
              data-active={on ? "true" : "false"}
              aria-pressed={on}
              onClick={() => onSelect(row.regime)}
            >
              <span className="ds-reg-hist-sat__dot" aria-hidden />
              <span className="ds-reg-hist-sat__lab">{row.label}</span>
              <span className="ds-reg-hist-sat__pct">{formatSharePct(row.pct)}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
