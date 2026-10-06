"use client";

import type { CSSProperties } from "react";

import {
  nowcastFocusBlurb,
  type NowcastProb,
} from "@/design/patterns/regime-nowcast/nowcast-utils";

type RegimeNowcastFocusProps = {
  row: NowcastProb | null;
  liveRegime: string;
};

export function RegimeNowcastFocus({ row, liveRegime }: RegimeNowcastFocusProps) {
  if (!row) return null;

  return (
    <div
      key={row.regime}
      className="ds-reg-now-focus"
      style={{ ["--ds-reg-tone" as string]: row.color } as CSSProperties}
      role="status"
    >
      <p className="ds-reg-now-focus__copy">
        <strong>{row.label} · live probability</strong>
        <span>{nowcastFocusBlurb(row, liveRegime)}</span>
      </p>
    </div>
  );
}
