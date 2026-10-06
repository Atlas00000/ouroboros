"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { ChartFrame, useChartTheme } from "@/design/patterns/charts";
import type { WeeklyReportItem } from "@/lib/api/types";

type ScoringSymbolBarsProps = {
  week: WeeklyReportItem | null;
};

/** Per-symbol hit rate for one week — Recharts. */
export function ScoringSymbolBars({ week }: ScoringSymbolBarsProps) {
  const { theme, reduceMotion } = useChartTheme();

  if (!week?.by_symbol_tf.length) {
    return (
      <ChartFrame
        title="By symbol"
        empty
        emptyMessage="No per-symbol breakdown in this report."
      />
    );
  }

  const data = week.by_symbol_tf.map((row) => ({
    key: `${row.symbol} ${row.timeframe}`,
    accuracy: row.accuracy != null ? Math.round(row.accuracy * 1000) / 10 : 0,
    n: row.n,
  }));

  return (
    <ChartFrame
      title={`By symbol · ${week.week_start.slice(0, 10)}`}
      meta={
        <span className="font-[family-name:var(--ds-font-numeric)] text-[length:var(--ds-text-micro)] text-ds-ink-muted">
          {week.n_correct}/{week.n_scored}
          {week.accuracy != null ? ` · ${(week.accuracy * 100).toFixed(1)}%` : ""}
        </span>
      }
    >
      <div className="h-56 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 40 }}>
            <CartesianGrid stroke={theme.line} strokeDasharray="3 6" vertical={false} />
            <XAxis
              dataKey="key"
              interval={0}
              angle={-35}
              textAnchor="end"
              height={50}
              tick={{ fill: theme.inkMuted, fontSize: 9 }}
              axisLine={{ stroke: theme.line }}
              tickLine={false}
            />
            <YAxis
              domain={[0, 100]}
              width={36}
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
              formatter={(value, _n, item) => [
                `${value}% (n=${(item?.payload as { n?: number })?.n ?? "—"})`,
                "Hit rate",
              ]}
            />
            <Bar
              dataKey="accuracy"
              fill={theme.signal}
              isAnimationActive={!reduceMotion}
              radius={[2, 2, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </ChartFrame>
  );
}
