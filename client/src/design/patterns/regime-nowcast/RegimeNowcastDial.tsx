"use client";

import type { CSSProperties } from "react";

import { NumberTick } from "@/design/motion/NumberTick";
import {
  formatProbPct,
  type NowcastProb,
} from "@/design/patterns/regime-nowcast/nowcast-utils";

const R = 36;
const C = 2 * Math.PI * R;

type RegimeNowcastDialProps = {
  rows: NowcastProb[];
  active: NowcastProb | null;
  liveRegime: string;
  onSelect: (regime: string) => void;
};

export function RegimeNowcastDial({
  rows,
  active,
  liveRegime,
  onSelect,
}: RegimeNowcastDialProps) {
  const pct = active?.pct ?? 0;
  const offset = C * (1 - Math.max(0, Math.min(100, pct)) / 100);

  return (
    <div className="ds-reg-now-dial">
      <div
        className="ds-reg-now-dial__ring"
        style={{ ["--ds-reg-tone" as string]: active?.color ?? "var(--ds-signal)" } as CSSProperties}
      >
        <svg className="ds-reg-now-dial__svg" viewBox="0 0 88 88" aria-hidden>
          <circle className="ds-reg-now-dial__track" cx="44" cy="44" r={R} />
          <circle
            className="ds-reg-now-dial__arc"
            cx="44"
            cy="44"
            r={R}
            style={
              {
                strokeDasharray: C,
                strokeDashoffset: offset,
                ["--ds-reg-now-circ" as string]: String(C),
                ["--ds-reg-now-offset" as string]: String(offset),
              } as CSSProperties
            }
          />
        </svg>
        <div className="ds-reg-now-dial__core">
          <p className="ds-reg-now-dial__pct">
            <NumberTick value={active ? formatProbPct(pct) : null} />
          </p>
          <p className="ds-reg-now-dial__name">{active?.label ?? "—"}</p>
        </div>
      </div>
      <div className="ds-reg-now-dial__sats" role="list" aria-label="Live probabilities">
        {rows.map((row) => {
          const on = row.regime === active?.regime;
          const live = row.regime === liveRegime;
          return (
            <button
              key={row.regime}
              type="button"
              role="listitem"
              className="ds-reg-now-sat"
              style={{ ["--ds-reg-tone" as string]: row.color } as CSSProperties}
              data-active={on ? "true" : "false"}
              data-live={live ? "true" : "false"}
              aria-pressed={on}
              onClick={() => onSelect(row.regime)}
            >
              <span className="ds-reg-now-sat__dot" aria-hidden />
              <span className="ds-reg-now-sat__lab">
                {row.label}
                {live ? " · live" : ""}
              </span>
              <span className="ds-reg-now-sat__pct">{formatProbPct(row.pct)}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
