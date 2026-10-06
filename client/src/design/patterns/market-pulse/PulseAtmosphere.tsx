"use client";

import { useId } from "react";

import type { PulseFocus } from "@/design/patterns/market-pulse/types";

type PulseAtmosphereProps = {
  focus: PulseFocus;
};

/**
 * Pointer-reactive ledger atmosphere — token washes + signal horizon.
 * No orbs, mesh clip-art, emoji, or illustration.
 */
export function PulseAtmosphere({ focus }: PulseAtmosphereProps) {
  const gradId = useId().replace(/:/g, "");

  return (
    <div className="ds-market-pulse__atmosphere" data-focus={focus} aria-hidden>
      <div className="ds-market-pulse__wash ds-market-pulse__wash--a" />
      <div className="ds-market-pulse__wash ds-market-pulse__wash--b" />
      <div className="ds-market-pulse__wash ds-market-pulse__wash--pointer" />

      <svg
        className="ds-market-pulse__horizon"
        viewBox="0 0 1400 220"
        preserveAspectRatio="none"
      >
        <defs>
          <linearGradient id={`${gradId}-stroke`} x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="var(--ds-pulse-tone)" stopOpacity="0" />
            <stop offset="22%" stopColor="var(--ds-pulse-tone)" stopOpacity="0.55" />
            <stop offset="55%" stopColor="var(--ds-pulse-tone)" stopOpacity="0.2" />
            <stop offset="100%" stopColor="var(--ds-pulse-tone)" stopOpacity="0" />
          </linearGradient>
          <linearGradient id={`${gradId}-fill`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="var(--ds-pulse-tone)" stopOpacity="0.14" />
            <stop offset="100%" stopColor="var(--ds-pulse-tone)" stopOpacity="0" />
          </linearGradient>
        </defs>
        <path
          className="ds-market-pulse__horizon-fill"
          d="M0 150 C180 110 320 190 480 130 S780 70 960 120 S1220 170 1400 110 L1400 220 L0 220 Z"
          fill={`url(#${gradId}-fill)`}
        />
        <path
          className="ds-market-pulse__horizon-stroke"
          d="M0 150 C180 110 320 190 480 130 S780 70 960 120 S1220 170 1400 110"
          fill="none"
          stroke={`url(#${gradId}-stroke)`}
          strokeWidth="1.6"
        />
        <g className="ds-market-pulse__ticks" stroke="var(--ds-line-strong)" strokeWidth="1">
          {Array.from({ length: 24 }, (_, i) => {
            const x = 40 + i * 56;
            const h = i % 4 === 0 ? 18 : i % 2 === 0 ? 11 : 6;
            return <line key={x} x1={x} y1={210} x2={x} y2={210 - h} />;
          })}
        </g>
      </svg>

      <div className="ds-market-pulse__veil" />
    </div>
  );
}
