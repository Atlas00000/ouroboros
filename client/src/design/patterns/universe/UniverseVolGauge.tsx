"use client";

import { useMemo } from "react";
import { Cell, Pie, PieChart, ResponsiveContainer } from "recharts";

import { cn } from "@/lib/utils";

type UniverseVolGaugeProps = {
  value?: number | null;
  className?: string;
};

/** Compact vol percentile ring (Recharts) — institutional, not clip art. */
export function UniverseVolGauge({ value, className }: UniverseVolGaugeProps) {
  const clamped =
    value == null || Number.isNaN(value) ? null : Math.max(0, Math.min(100, value));
  const hot = clamped != null && clamped >= 75;

  const data = useMemo(() => {
    if (clamped == null) return [{ name: "empty", value: 1 }];
    return [
      { name: "vol", value: clamped },
      { name: "rest", value: Math.max(0.01, 100 - clamped) },
    ];
  }, [clamped]);

  return (
    <div
      className={cn("ds-universe-vol-gauge", className)}
      data-hot={hot ? "true" : "false"}
      data-empty={clamped == null ? "true" : "false"}
    >
      <div className="ds-universe-vol-gauge__ring" aria-hidden>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              dataKey="value"
              startAngle={90}
              endAngle={-270}
              innerRadius="68%"
              outerRadius="92%"
              stroke="none"
              isAnimationActive={false}
            >
              <Cell
                fill={
                  clamped == null
                    ? "var(--ds-line)"
                    : hot
                      ? "var(--ds-vol)"
                      : "var(--ds-signal)"
                }
              />
              <Cell fill="var(--ds-line)" />
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        <span className="ds-universe-vol-gauge__value">
          {clamped == null ? "—" : `${Math.round(clamped)}`}
        </span>
      </div>
      <span className="ds-universe-vol-gauge__label">vol %</span>
    </div>
  );
}
