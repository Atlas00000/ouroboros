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

type OutboxMixProps = {
  unpublished: number;
  published: number;
};

/** Outbox unpublished vs published — Recharts. */
export function OutboxMix({ unpublished, published }: OutboxMixProps) {
  const { theme, reduceMotion } = useChartTheme();
  const data = [
    { key: "Unpublished", value: unpublished, fill: theme.warn },
    { key: "Published", value: published, fill: theme.ok },
  ];

  return (
    <ChartFrame title="Outbox mix">
      <div className="h-40 w-full">
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
              width={40}
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
