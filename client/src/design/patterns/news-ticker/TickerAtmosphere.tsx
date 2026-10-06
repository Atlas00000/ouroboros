"use client";

import { useId } from "react";

type TickerAtmosphereProps = {
  focusLevel?: string;
  focusSymbol?: string | null;
};

/**
 * Drivers atmosphere — focus wash + ledger ticks.
 * No orbs, mesh clip-art, emoji, or illustration.
 */
export function TickerAtmosphere({ focusLevel, focusSymbol }: TickerAtmosphereProps) {
  const uid = useId().replace(/:/g, "");

  return (
    <div
      className="ds-ticker__atmosphere"
      data-level={focusLevel ?? "unknown"}
      aria-hidden
    >
      <div className="ds-ticker__wash ds-ticker__wash--base" />
      <div className="ds-ticker__wash ds-ticker__wash--focus" />
      <svg className="ds-ticker__ticks" viewBox="0 0 40 400" preserveAspectRatio="none">
        <defs>
          <linearGradient id={`${uid}-tick`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="var(--ds-ticker-focus, var(--ds-signal))" stopOpacity="0" />
            <stop offset="50%" stopColor="var(--ds-ticker-focus, var(--ds-signal))" stopOpacity="0.55" />
            <stop offset="100%" stopColor="var(--ds-ticker-focus, var(--ds-signal))" stopOpacity="0" />
          </linearGradient>
        </defs>
        {Array.from({ length: 28 }, (_, i) => {
          const y = 12 + i * 14;
          const w = i % 4 === 0 ? 18 : i % 2 === 0 ? 11 : 6;
          return (
            <line
              key={y}
              x1="0"
              y1={y}
              x2={w}
              y2={y}
              stroke={`url(#${uid}-tick)`}
              strokeWidth="1"
            />
          );
        })}
      </svg>
      {focusSymbol ? (
        <p className="ds-ticker__symbol-ghost">{focusSymbol}</p>
      ) : (
        <p className="ds-ticker__symbol-ghost">DRV</p>
      )}
    </div>
  );
}
