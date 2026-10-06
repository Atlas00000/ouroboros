"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ComposedChart,
  Customized,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import {
  DS_CHART_DEFAULT,
  DS_CHART_LABEL,
  type DsChartType,
} from "@/design/patterns/charts/chart-types";
import { ChartFrame, useChartTheme } from "@/design/patterns/charts";
import { cssVarStroke } from "@/design/patterns/charts/theme";
import { toneForRegime, type Regime } from "@/design/map/backend-visual";
import { PriceChartType } from "@/design/patterns/price-regime/PriceChartType";
import { PriceTimeframe } from "@/design/patterns/price-regime/PriceTimeframe";
import { RegimeBandLayer } from "@/design/patterns/price-regime/RegimeBandLayer";
import {
  ASSET_BAR_DEFAULT,
  ASSET_BAR_LABEL,
  type AssetBarTimeframe,
} from "@/design/patterns/price-regime/timeframes";
import type { BarPoint, BarsResponse } from "@/lib/queries/asset-detail";

import "./price-regime.css";

export type PriceRegimeChartProps = {
  symbol: string;
  initialBars?: BarPoint[];
  initialTimeframe?: AssetBarTimeframe;
  regime?: string | null;
  stale?: boolean;
};

type Row = {
  ts: string;
  label: string;
  open: number;
  high: number;
  low: number;
  close: number;
};

function formatClose(n: number): string {
  if (Math.abs(n) >= 1000) return n.toFixed(2);
  if (Math.abs(n) >= 1) return n.toFixed(5);
  return n.toPrecision(6);
}

type AxisLike = {
  scale: ((v: string | number) => number) & { bandwidth?: () => number };
};

/** Draw OHLC candles using Recharts axis scales. */
function PriceCandlesLayer(props: Record<string, unknown>) {
  const xAxisMap = props.xAxisMap as Record<string, AxisLike> | undefined;
  const yAxisMap = props.yAxisMap as Record<string, AxisLike> | undefined;
  const data = props.data as Row[] | undefined;

  const xAxis = xAxisMap ? Object.values(xAxisMap)[0] : undefined;
  const yAxis = yAxisMap ? Object.values(yAxisMap)[0] : undefined;
  if (!xAxis?.scale || !yAxis?.scale || !data?.length) return null;

  const bandwidth =
    typeof xAxis.scale.bandwidth === "function"
      ? Math.max(2, xAxis.scale.bandwidth())
      : Math.max(2, 120 / Math.max(data.length, 1));
  const bodyW = Math.max(1.5, Math.min(bandwidth * 0.62, 12));

  return (
    <g className="ds-price-candles" pointerEvents="none">
      {data.map((d) => {
        const x0 = xAxis.scale(d.label);
        const cx = x0 + bandwidth / 2;
        const yOpen = yAxis.scale(d.open);
        const yClose = yAxis.scale(d.close);
        const yHigh = yAxis.scale(d.high);
        const yLow = yAxis.scale(d.low);
        const up = d.close >= d.open;
        const top = Math.min(yOpen, yClose);
        const bodyH = Math.max(1, Math.abs(yClose - yOpen));
        return (
          <g key={d.ts} data-tone={up ? "up" : "down"}>
            <line
              className="ds-price-candles__wick"
              x1={cx}
              x2={cx}
              y1={yHigh}
              y2={yLow}
            />
            <rect
              className="ds-price-candles__body"
              x={cx - bodyW / 2}
              y={top}
              width={bodyW}
              height={bodyH}
            />
          </g>
        );
      })}
    </g>
  );
}

/**
 * Asset price path — Recharts close series or OHLC candles + D3 regime wash.
 */
export function PriceRegimeChart({
  symbol,
  initialBars = [],
  initialTimeframe = ASSET_BAR_DEFAULT,
  regime,
  stale,
}: PriceRegimeChartProps) {
  const [timeframe, setTimeframe] = useState<AssetBarTimeframe>(initialTimeframe);
  const [chartType, setChartType] = useState<DsChartType>(DS_CHART_DEFAULT);
  const { theme, reduceMotion } = useChartTheme();
  const stroke = cssVarStroke(toneForRegime(regime as Regime));
  const plotRef = useRef<HTMLDivElement | null>(null);
  const [size, setSize] = useState({ w: 0, h: 220 });

  useEffect(() => {
    const el = plotRef.current;
    if (!el) return;
    const ro = new ResizeObserver((entries) => {
      const cr = entries[0]?.contentRect;
      if (cr) setSize({ w: cr.width, h: cr.height });
    });
    ro.observe(el);
    setSize({ w: el.clientWidth, h: el.clientHeight || 220 });
    return () => ro.disconnect();
  }, []);

  const seeded =
    timeframe === initialTimeframe && initialBars.length >= 2;

  const q = useQuery({
    queryKey: ["asset-bars", symbol, timeframe],
    enabled: !seeded,
    staleTime: 60_000,
    queryFn: async (): Promise<BarsResponse> => {
      const params = new URLSearchParams({ symbol, timeframe });
      const res = await fetch(`/api/asset-bars?${params}`, { cache: "no-store" });
      if (!res.ok) throw new Error(`bars ${res.status}`);
      return (await res.json()) as BarsResponse;
    },
  });

  const bars = seeded ? initialBars : (q.data?.bars ?? []);
  const loading = !seeded && q.isLoading;
  const chartStale = seeded ? stale : Boolean(q.data?.provenance?.stale ?? stale);

  const data = useMemo<Row[]>(
    () =>
      bars.map((b) => {
        const ts = typeof b.ts === "string" ? b.ts : String(b.ts);
        return {
          ts,
          label: ts.slice(0, 16),
          open: b.open,
          high: b.high,
          low: b.low,
          close: b.close,
        };
      }),
    [bars],
  );

  const yDomain = useMemo<[number, number]>(() => {
    if (!data.length) return [0, 1];
    const lo = Math.min(...data.map((d) => d.low));
    const hi = Math.max(...data.map((d) => d.high));
    const pad = (hi - lo) * 0.04 || Math.abs(hi) * 0.001 || 1;
    return [lo - pad, hi + pad];
  }, [data]);

  const last = data.length ? data[data.length - 1].close : null;
  const first = data.length ? data[0].close : null;
  const changePct =
    first != null && last != null && first !== 0
      ? ((last - first) / first) * 100
      : null;

  const axisStroke = theme.line;
  const tickFill = theme.inkMuted;

  return (
    <ChartFrame
      title={`Price · ${ASSET_BAR_LABEL[timeframe]} · ${DS_CHART_LABEL[chartType]}`}
      stale={chartStale}
      loading={loading}
      empty={!loading && data.length < 2}
      emptyMessage={`No ${ASSET_BAR_LABEL[timeframe]} series`}
      meta={
        <div className="ds-price-regime__meta">
          <PriceTimeframe value={timeframe} onChange={setTimeframe} />
          <PriceChartType value={chartType} onChange={setChartType} />
          {last != null ? (
            <span className="ds-price-regime__last">
              {formatClose(last)}
              {changePct != null ? (
                <span
                  data-tone={
                    changePct > 0 ? "up" : changePct < 0 ? "down" : "flat"
                  }
                >
                  {" "}
                  {changePct > 0 ? "+" : ""}
                  {changePct.toFixed(2)}%
                </span>
              ) : null}
            </span>
          ) : null}
        </div>
      }
      className="ds-price-regime"
    >
      <div className="ds-price-regime__plot" ref={plotRef}>
        <RegimeBandLayer regime={regime} width={size.w} height={size.h} />
        <ResponsiveContainer width="100%" height="100%">
          {chartType === "candles" ? (
            <ComposedChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
              <CartesianGrid stroke={axisStroke} strokeDasharray="3 6" vertical={false} />
              <XAxis
                dataKey="label"
                tick={{ fill: tickFill, fontSize: 10 }}
                axisLine={{ stroke: axisStroke }}
                tickLine={false}
                minTickGap={48}
              />
              <YAxis
                domain={yDomain}
                width={64}
                tick={{ fill: tickFill, fontSize: 10 }}
                axisLine={false}
                tickLine={false}
                tickFormatter={(v) => formatClose(Number(v))}
              />
              <Tooltip
                cursor={{ stroke: theme.lineStrong, strokeWidth: 1 }}
                contentStyle={{
                  background: theme.planeRaised,
                  border: `1px solid ${theme.line}`,
                  borderRadius: 0,
                  fontFamily: "var(--ds-font-numeric)",
                  fontSize: 11,
                  color: theme.ink,
                }}
                labelFormatter={(_, payload) =>
                  (payload?.[0]?.payload as Row | undefined)?.ts ?? ""
                }
                formatter={(value) => {
                  const n = typeof value === "number" ? value : Number(value);
                  return [Number.isFinite(n) ? formatClose(n) : "—", "Close"];
                }}
              />
              <Line
                type="monotone"
                dataKey="close"
                stroke="transparent"
                strokeWidth={0}
                dot={false}
                activeDot={{ r: 3, fill: stroke, stroke: theme.canvas, strokeWidth: 1 }}
                isAnimationActive={false}
                legendType="none"
              />
              <Customized component={PriceCandlesLayer} />
            </ComposedChart>
          ) : (
            <AreaChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="ds-price-fill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={stroke} stopOpacity={0.28} />
                  <stop offset="100%" stopColor={stroke} stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke={axisStroke} strokeDasharray="3 6" vertical={false} />
              <XAxis
                dataKey="label"
                tick={{ fill: tickFill, fontSize: 10 }}
                axisLine={{ stroke: axisStroke }}
                tickLine={false}
                minTickGap={48}
              />
              <YAxis
                domain={yDomain}
                width={64}
                tick={{ fill: tickFill, fontSize: 10 }}
                axisLine={false}
                tickLine={false}
                tickFormatter={(v) => formatClose(Number(v))}
              />
              <Tooltip
                cursor={{ stroke: theme.lineStrong, strokeWidth: 1 }}
                contentStyle={{
                  background: theme.planeRaised,
                  border: `1px solid ${theme.line}`,
                  borderRadius: 0,
                  fontFamily: "var(--ds-font-numeric)",
                  fontSize: 11,
                  color: theme.ink,
                }}
                labelFormatter={(_, payload) =>
                  (payload?.[0]?.payload as Row | undefined)?.ts ?? ""
                }
                formatter={(value) => {
                  const n = typeof value === "number" ? value : Number(value);
                  return [Number.isFinite(n) ? formatClose(n) : "—", "Close"];
                }}
              />
              <Area
                type="monotone"
                dataKey="close"
                stroke={stroke}
                strokeWidth={1.6}
                fill="url(#ds-price-fill)"
                isAnimationActive={!reduceMotion}
                dot={false}
                activeDot={{ r: 3, fill: stroke, stroke: theme.canvas, strokeWidth: 1 }}
              />
            </AreaChart>
          )}
        </ResponsiveContainer>
      </div>
    </ChartFrame>
  );
}
