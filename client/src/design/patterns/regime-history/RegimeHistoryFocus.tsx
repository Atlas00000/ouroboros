"use client";

import type { CSSProperties } from "react";

import {
  historyFocusBlurb,
  type RegimeShareRow,
} from "@/design/patterns/regime-history/regime-history-utils";

type RegimeHistoryFocusProps = {
  row: RegimeShareRow | null;
};

/** Copy-only focus strip — dial owns the oversized share readout. */
export function RegimeHistoryFocus({ row }: RegimeHistoryFocusProps) {
  if (!row) return null;

  return (
    <div
      key={row.regime}
      className="ds-reg-hist-focus ds-reg-hist-focus--copy"
      style={{ ["--ds-reg-tone" as string]: row.color } as CSSProperties}
      role="status"
    >
      <p className="ds-reg-hist-focus__copy">
        <strong>{row.label} · history share</strong>
        <span>{historyFocusBlurb(row)}</span>
      </p>
    </div>
  );
}
