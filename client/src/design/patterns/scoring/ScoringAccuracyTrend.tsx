"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { ChartFrame, useChartTheme } from "@/design/patterns/charts";
import type { WeeklyReportItem } from "@/lib/api/types";

type ScoringAccuracyTrendProps = {
  items: WeeklyReportItem[];
};

/** Weekly hit-rate trend — Recharts. */
export function ScoringAccuracyTrend({ items }: ScoringAccuracyTrendProps) {
  const { theme, reduceMotion } = useChartTheme();
  const data = [...items]
    .slice()
    .reverse()
    .map((w) => ({
      week: w.week_start.slice(0, 10),
      accuracy: w.accuracy != null ? Math.round(w.accuracy * 1000) / 10 : null,
      n: w.n_scored,
    }))
    .filter((d) => d.accuracy != null);

  if (!data.length) {
    return (
      <ChartFrame
        title="Weekly accuracy"
        empty
        emptyMessage="No scored weeks with accuracy yet."
      />
    );
  }

  return (
    <ChartFrame title="Weekly accuracy">
      <div className="h-48 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="ds-score-fill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={theme.signal} stopOpacity={0.3} />
                <stop offset="100%" stopColor={theme.signal} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke={theme.line} strokeDasharray="3 6" vertical={false} />
            <XAxis
              dataKey="week"
              tick={{ fill: theme.inkMuted, fontSize: 10 }}
              axisLine={{ stroke: theme.line }}
              tickLine={false}
              minTickGap={24}
            />
            <YAxis
              domain={[0, 100]}
              width={40}
              tick={{ fill: theme.inkMuted, fontSize: 10 }}
              axisLine={false}
              tickLine={false}
              unit="%"
            />
            <Tooltip
              contentStyle={{
                background: theme.planeRaised,
                border: `1px solid ${theme.line}`,
                borderRadius: 0,
                fontSize: 11,
                color: theme.ink,
              }}
              formatter={(value) => [`${value}%`, "Accuracy"]}
            />
            <Area
              type="monotone"
              dataKey="accuracy"
              stroke={theme.signal}
              strokeWidth={1.6}
              fill="url(#ds-score-fill)"
              isAnimationActive={!reduceMotion}
              connectNulls
              dot={{ r: 2, fill: theme.signal }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </ChartFrame>
  );
}
