"use client";

import type { CSSProperties } from "react";

import { cssVarForTone, REGIME_LABEL, toneForRegime } from "@/design/map/backend-visual";
import {
  PULSE_REGIME_ORDER,
  type PulseFocus,
  type PulseRegimeMix,
} from "@/design/patterns/market-pulse/types";
import { cn } from "@/lib/utils";

type PulseSpectrumProps = {
  mix: PulseRegimeMix;
  focus: PulseFocus;
  onFocus: (focus: PulseFocus) => void;
  totalAssets: number;
};

/**
 * Interactive regime intensity strip — ink columns, not a boxed bar chart.
 */
export function PulseSpectrum({
  mix,
  focus,
  onFocus,
  totalAssets,
}: PulseSpectrumProps) {
  const denom = Math.max(totalAssets, 1);

  return (
    <div
      className="ds-pulse-spectrum"
      role="radiogroup"
      aria-label="Regime mix on desk"
    >
      <div className="ds-pulse-spectrum__head">
        <span className="ds-pulse-spectrum__eyebrow">Regime mix</span>
        <span className="ds-pulse-spectrum__hint">Select a band to recolour the desk</span>
      </div>
      <div className="ds-pulse-spectrum__row">
        {PULSE_REGIME_ORDER.map((key) => {
          const count = mix[key];
          const share = count / denom;
          const active = focus === key;
          const tone = cssVarForTone(toneForRegime(key));
          return (
            <button
              key={key}
              type="button"
              role="radio"
              aria-checked={active}
              className={cn("ds-pulse-spectrum__band", active && "is-active")}
              style={
                {
                  ["--ds-band-tone" as string]: tone,
                  ["--ds-band-share" as string]: String(Math.max(0.08, share)),
                } as CSSProperties
              }
              onClick={() => onFocus(key)}
            >
              <span className="ds-pulse-spectrum__column" aria-hidden />
              <span className="ds-pulse-spectrum__meta">
                <span className="ds-pulse-spectrum__label">
                  {REGIME_LABEL[key] ?? key}
                </span>
                <span className="ds-pulse-spectrum__count">{count}</span>
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
