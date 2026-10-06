"use client";

import { useEffect, useRef } from "react";
import * as d3 from "d3";

import { cssVarStroke, useChartTheme } from "@/design/patterns/charts";
import { toneForRegime, type Regime } from "@/design/map/backend-visual";

type RegimeBandLayerProps = {
  regime?: string | null;
  width: number;
  height: number;
};

/** D3 soft regime wash behind the price series — token fill only. */
export function RegimeBandLayer({ regime, width, height }: RegimeBandLayerProps) {
  const ref = useRef<SVGSVGElement | null>(null);
  const { reduceMotion } = useChartTheme();
  const fill = cssVarStroke(toneForRegime(regime as Regime));

  useEffect(() => {
    const svg = d3.select(ref.current);
    svg.selectAll("*").remove();
    if (width <= 0 || height <= 0) return;

    const g = svg.attr("width", width).attr("height", height).append("g");

    const rect = g
      .append("rect")
      .attr("x", 0)
      .attr("y", 0)
      .attr("width", width)
      .attr("height", height)
      .attr("fill", fill)
      .attr("opacity", 0);

    if (reduceMotion) {
      rect.attr("opacity", 0.08);
    } else {
      rect.transition().duration(280).attr("opacity", 0.08);
    }
  }, [fill, width, height, reduceMotion, regime]);

  return (
    <svg
      ref={ref}
      className="ds-price-regime__bands"
      aria-hidden
      style={{ position: "absolute", inset: 0, width: "100%", height: "100%", pointerEvents: "none" }}
    />
  );
}
