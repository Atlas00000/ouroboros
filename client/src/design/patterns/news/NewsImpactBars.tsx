"use client";

import {
  Bar,
  BarChart,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { ChartFrame, useChartTheme } from "@/design/patterns/charts";
import {
  impactLabel,
  normalizeImpact,
  type ImpactLevel,
} from "@/design/patterns/news-ticker/TickerImpact";
import type { NewsListItem } from "@/lib/api/types";

type NewsImpactBarsProps = {
  items: NewsListItem[];
};

/** Impact distribution for the current news cut — Recharts. */
export function NewsImpactBars({ items }: NewsImpactBarsProps) {
  const { theme, reduceMotion } = useChartTheme();

  const counts: Record<ImpactLevel, number> = {
    high: 0,
    medium: 0,
    low: 0,
    unknown: 0,
  };
  for (const n of items) {
    counts[normalizeImpact(n.impact)] += 1;
  }

  const data = (["high", "medium", "low", "unknown"] as ImpactLevel[]).map((level) => ({
    key: impactLabel(level),
    value: counts[level],
    fill:
      level === "high"
        ? theme.halt
        : level === "medium"
          ? theme.warn
          : level === "low"
            ? theme.signal
            : theme.idle,
  }));

  if (!items.length) {
    return null;
  }

  return (
    <ChartFrame title="Impact mix" meta={<span className="text-[10px] text-ds-ink-faint">{items.length} headlines</span>}>
      <div className="h-36 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
            <XAxis
              dataKey="key"
              tick={{ fill: theme.inkMuted, fontSize: 11 }}
              axisLine={{ stroke: theme.line }}
              tickLine={false}
            />
            <YAxis
              allowDecimals={false}
              width={28}
              tick={{ fill: theme.inkMuted, fontSize: 10 }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              contentStyle={{
                background: theme.planeRaised,
                border: `1px solid ${theme.line}`,
                borderRadius: 0,
                fontSize: 11,
                color: theme.ink,
              }}
            />
            <Bar dataKey="value" isAnimationActive={!reduceMotion} radius={[2, 2, 0, 0]}>
              {data.map((d) => (
                <Cell key={d.key} fill={d.fill} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </ChartFrame>
  );
}
