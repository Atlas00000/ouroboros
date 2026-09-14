"use client";

import { useMemo } from "react";

import { StateBadge } from "@/components/StateBadge";
import { StaleBadge } from "@/components/StaleBadge";
import type { BarPoint } from "@/lib/queries/asset-detail";
import { cn } from "@/lib/utils";

const REGIME_FILL: Record<string, string> = {
  trending_up: "var(--regime-trending-up)",
  trending_down: "var(--regime-trending-down)",
  ranging: "var(--regime-ranging)",
  high_volatility: "var(--regime-high-vol)",
};

type Props = {
  bars: BarPoint[];
  regime?: string | null;
  stale?: boolean;
  className?: string;
};

/** SVG close series — Lightweight Charts can replace this without API changes. */
export function PriceChart({ bars, regime, stale, className }: Props) {
  const path = useMemo(() => {
    if (bars.length < 2) return "";
    const closes = bars.map((b) => b.close);
    const min = Math.min(...closes);
    const max = Math.max(...closes);
    const span = max - min || 1;
    const w = 600;
    const h = 180;
    const pad = 8;
    return closes
      .map((c, i) => {
        const x = pad + (i / (closes.length - 1)) * (w - pad * 2);
        const y = pad + (1 - (c - min) / span) * (h - pad * 2);
        return `${i === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
      })
      .join(" ");
  }, [bars]);

  const last = bars.length ? bars[bars.length - 1] : null;
  const band = REGIME_FILL[regime ?? ""] ?? "transparent";

  return (
    <section className={cn("rounded-md border border-border bg-card p-3", className)}>
      <div className="mb-2 flex flex-wrap items-center gap-2">
        <h2 className="text-sm font-medium text-foreground">Price · H1</h2>
        <StateBadge regime={regime} />
        <StaleBadge stale={stale} />
        {last ? (
          <span className="ml-auto tabular-nums text-xs text-muted">
            {last.close.toPrecision(6)} · {last.ts}
          </span>
        ) : null}
      </div>
      {!bars.length ? (
        <p className="py-10 text-center text-sm text-muted">No bars available.</p>
      ) : (
        <div className="relative overflow-hidden rounded" style={{ background: `${band}18` }}>
          <svg viewBox="0 0 600 180" className="h-44 w-full" role="img" aria-label="Close price series">
            <RegimeBands regime={regime} />
            <path d={path} fill="none" stroke="currentColor" strokeWidth="1.5" className="text-foreground" />
          </svg>
        </div>
      )}
    </section>
  );
}

export function RegimeBands({ regime }: { regime?: string | null }) {
  if (!regime) return null;
  const color = REGIME_FILL[regime] ?? "var(--regime-ranging)";
  return <rect x="0" y="0" width="600" height="180" fill={color} opacity="0.08" />;
}
