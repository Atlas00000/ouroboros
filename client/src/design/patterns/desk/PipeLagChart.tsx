"use client";

import { useEffect, useRef } from "react";
import * as d3 from "d3";

import { ChartFrame, useChartTheme } from "@/design/patterns/charts";
import type { OpsSummaryResponse } from "@/lib/api/types";

type PipeLagChartProps = {
  lag: OpsSummaryResponse["ingestion_lag"];
};

const WARN_S = 300;
const HALT_S = 3600;

/** Ingestion lag horizon — D3 bars with warn/halt thresholds. */
export function PipeLagChart({ lag }: PipeLagChartProps) {
  const ref = useRef<SVGSVGElement | null>(null);
  const { theme, reduceMotion } = useChartTheme();

  useEffect(() => {
    const svg = d3.select(ref.current);
    svg.selectAll("*").remove();
    if (!lag.length) return;

    const width = ref.current?.clientWidth || 360;
    const rowH = 26;
    const labelW = 120;
    const height = lag.length * rowH + 16;
    svg.attr("viewBox", `0 0 ${width} ${height}`).attr("height", height);

    const maxAge = d3.max(lag, (d) => d.age_seconds ?? 0) ?? 1;
    const x = d3
      .scaleLinear()
      .domain([0, Math.max(maxAge, HALT_S)])
      .range([labelW, width - 8]);

    const g = svg.append("g");

    // threshold guides
    [WARN_S, HALT_S].forEach((t, i) => {
      g.append("line")
        .attr("x1", x(t))
        .attr("x2", x(t))
        .attr("y1", 0)
        .attr("y2", height)
        .attr("stroke", i === 0 ? theme.warn : theme.halt)
        .attr("stroke-opacity", 0.45)
        .attr("stroke-dasharray", "3 4");
    });

    lag.forEach((row, i) => {
      const age = row.age_seconds ?? 0;
      const y = i * rowH + 4;
      const fill =
        age >= HALT_S ? theme.halt : age >= WARN_S ? theme.warn : theme.signal;

      g.append("text")
        .attr("x", 0)
        .attr("y", y + rowH / 2)
        .attr("dominant-baseline", "middle")
        .attr("fill", theme.inkMuted)
        .attr("font-family", "var(--ds-font-numeric)")
        .attr("font-size", 10)
        .text(row.source_id);

      const rect = g
        .append("rect")
        .attr("x", labelW)
        .attr("y", y + 6)
        .attr("height", rowH - 12)
        .attr("fill", fill)
        .attr("width", reduceMotion ? Math.max(2, x(age) - labelW) : 0);

      if (!reduceMotion) {
        rect
          .transition()
          .duration(320)
          .attr("width", Math.max(2, x(age) - labelW));
      }

      g.append("text")
        .attr("x", width - 8)
        .attr("y", y + rowH / 2)
        .attr("text-anchor", "end")
        .attr("dominant-baseline", "middle")
        .attr("fill", theme.inkMuted)
        .attr("font-family", "var(--ds-font-numeric)")
        .attr("font-size", 10)
        .text(row.age_seconds != null ? `${Math.round(row.age_seconds)}s` : "never");
    });
  }, [lag, theme, reduceMotion]);

  if (!lag.length) {
    return (
      <ChartFrame title="Ingestion lag" empty emptyMessage="No lag rows in summary." />
    );
  }

  return (
    <ChartFrame
      title="Ingestion lag"
      meta={
        <span className="text-[10px] text-ds-ink-faint">
          Dashed · warn {WARN_S}s · halt {HALT_S}s
        </span>
      }
    >
      <svg ref={ref} className="w-full" role="img" aria-label="Ingestion lag by source" />
    </ChartFrame>
  );
}
