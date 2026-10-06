"use client";

import { useCallback, useId, useMemo, useState, type MouseEvent } from "react";
import {
  Area,
  AreaChart,
  ResponsiveContainer,
  Tooltip,
  YAxis,
} from "recharts";

import { cssVarForTone, toneForRegime, type Regime } from "@/design/map/backend-visual";
import {
  UNIVERSE_CHART_DEFAULT,
  type UniverseChartType,
  type UniverseSparkOhlc,
} from "@/design/patterns/universe/spark";
import { cn } from "@/lib/utils";

type UniverseMiniChartProps = {
  symbol: string;
  closes?: number[];
  bars?: UniverseSparkOhlc[];
  chartType?: UniverseChartType;
  regime?: string | null;
  loading?: boolean;
  timeframeLabel?: string;
  className?: string;
};

type Point = { i: number; close: number };

type PeekState = {
  close: number;
  changePct: number | null;
  open?: number;
  high?: number;
  low?: number;
};

const CANDLE_VIEW_W = 120;
const CANDLE_VIEW_H = 48;

function formatPx(n: number): string {
  if (!Number.isFinite(n)) return "—";
  if (Math.abs(n) >= 1000) return n.toFixed(1);
  if (Math.abs(n) >= 1) return n.toFixed(4);
  return n.toPrecision(5);
}

function formatChg(pct: number | null): string {
  if (pct == null || Number.isNaN(pct)) return "—";
  const sign = pct > 0 ? "+" : "";
  return `${sign}${pct.toFixed(2)}%`;
}

function chgTone(pct: number | null): "up" | "down" | "flat" {
  if (pct == null || Number.isNaN(pct) || pct === 0) return "flat";
  return pct > 0 ? "up" : "down";
}

function changeFromBase(value: number, base: number | undefined): number | null {
  if (base == null || !Number.isFinite(base) || base === 0) return null;
  return ((value - base) / base) * 100;
}

/** Compact corner peek — updates as the cursor scrubs the series. */
function ChartPeek({
  peek,
  timeframeLabel,
  detailed,
}: {
  peek: PeekState;
  timeframeLabel: string;
  detailed?: boolean;
}) {
  return (
    <div className="ds-universe-peek" role="status" aria-live="polite">
      {detailed && peek.open != null && peek.high != null && peek.low != null ? (
        <div className="ds-universe-peek__ohlc">
          <span>
            <em>O</em> {formatPx(peek.open)}
          </span>
          <span>
            <em>H</em> {formatPx(peek.high)}
          </span>
          <span>
            <em>L</em> {formatPx(peek.low)}
          </span>
          <span>
            <em>C</em> {formatPx(peek.close)}
          </span>
        </div>
      ) : (
        <span className="ds-universe-peek__px">{formatPx(peek.close)}</span>
      )}
      <div className="ds-universe-peek__meta">
        <span
          className="ds-universe-peek__chg"
          data-tone={chgTone(peek.changePct)}
        >
          {formatChg(peek.changePct)}
        </span>
        <span className="ds-universe-peek__tf">{timeframeLabel}</span>
      </div>
    </div>
  );
}

function MiniCandles({
  symbol,
  bars,
  timeframeLabel,
  hoverIndex,
  onHoverIndex,
}: {
  symbol: string;
  bars: UniverseSparkOhlc[];
  timeframeLabel: string;
  hoverIndex: number | null;
  onHoverIndex: (index: number | null) => void;
}) {
  const geometry = useMemo(() => {
    const min = Math.min(...bars.map((b) => b.low));
    const max = Math.max(...bars.map((b) => b.high));
    const range = max - min || 1;
    const pad = range * 0.06;
    const lo = min - pad;
    const hi = max + pad;
    const span = hi - lo || 1;
    const slot = CANDLE_VIEW_W / bars.length;
    const bodyW = Math.max(0.55, Math.min(2.4, slot * 0.55));

    const y = (v: number) =>
      CANDLE_VIEW_H - ((v - lo) / span) * CANDLE_VIEW_H;

    return bars.map((b, i) => {
      const up = b.close >= b.open;
      const cx = i * slot + slot / 2;
      const top = y(Math.max(b.open, b.close));
      const bot = y(Math.min(b.open, b.close));
      const bodyH = Math.max(0.6, bot - top);
      return {
        key: i,
        up,
        cx,
        wickTop: y(b.high),
        wickBot: y(b.low),
        bodyY: top,
        bodyH,
        bodyW,
        slot,
      };
    });
  }, [bars]);

  const onMove = useCallback(
    (e: MouseEvent<SVGSVGElement>) => {
      const rect = e.currentTarget.getBoundingClientRect();
      if (rect.width <= 0) return;
      const x = ((e.clientX - rect.left) / rect.width) * CANDLE_VIEW_W;
      const idx = Math.max(0, Math.min(bars.length - 1, Math.floor(x / (CANDLE_VIEW_W / bars.length))));
      onHoverIndex(idx);
    },
    [bars.length, onHoverIndex],
  );

  return (
    <svg
      className="ds-universe-candles"
      viewBox={`0 0 ${CANDLE_VIEW_W} ${CANDLE_VIEW_H}`}
      preserveAspectRatio="none"
      role="img"
      aria-label={`${symbol} ${timeframeLabel} candles, ${bars.length} bars`}
      onMouseMove={onMove}
      onMouseLeave={() => onHoverIndex(null)}
    >
      {hoverIndex != null ? (
        <rect
          className="ds-universe-candles__guide"
          x={geometry[hoverIndex].cx - geometry[hoverIndex].slot / 2}
          y={0}
          width={geometry[hoverIndex].slot}
          height={CANDLE_VIEW_H}
        />
      ) : null}
      {geometry.map((c, i) => (
        <g
          key={c.key}
          data-tone={c.up ? "up" : "down"}
          data-active={hoverIndex === i ? "true" : hoverIndex == null ? undefined : "false"}
        >
          <line
            className="ds-universe-candles__wick"
            x1={c.cx}
            x2={c.cx}
            y1={c.wickTop}
            y2={c.wickBot}
          />
          <rect
            className="ds-universe-candles__body"
            x={c.cx - c.bodyW / 2}
            y={c.bodyY}
            width={c.bodyW}
            height={c.bodyH}
          />
        </g>
      ))}
    </svg>
  );
}

/**
 * Universe tile chart — line (area) default, or OHLC candles.
 * Hover peeks a compact readout; real series only.
 */
export function UniverseMiniChart({
  symbol,
  closes,
  bars,
  chartType = UNIVERSE_CHART_DEFAULT,
  regime,
  loading,
  timeframeLabel = "15m",
  className,
}: UniverseMiniChartProps) {
  const gradId = useId().replace(/:/g, "");
  const tone = cssVarForTone(toneForRegime(regime as Regime));
  const data = useMemo<Point[]>(
    () => (closes ?? []).map((close, i) => ({ i, close })),
    [closes],
  );
  const candleBars = bars?.length ? bars : undefined;
  const [peek, setPeek] = useState<PeekState | null>(null);
  const [candleHover, setCandleHover] = useState<number | null>(null);

  const seriesOpen = data[0]?.close;
  const candleOpen = candleBars?.[0]?.close;

  const onLineMove = useCallback(
    (state: unknown) => {
      const payload = (
        state as { activePayload?: Array<{ value?: number | string }> } | null
      )?.activePayload?.[0]?.value;
      const close = typeof payload === "number" ? payload : Number(payload);
      if (!Number.isFinite(close)) return;
      setPeek({
        close,
        changePct: changeFromBase(close, seriesOpen),
      });
    },
    [seriesOpen],
  );

  const onCandleHover = useCallback(
    (index: number | null) => {
      setCandleHover(index);
      if (index == null || !candleBars?.[index]) {
        setPeek(null);
        return;
      }
      const b = candleBars[index];
      setPeek({
        close: b.close,
        open: b.open,
        high: b.high,
        low: b.low,
        changePct: changeFromBase(b.close, candleOpen),
      });
    },
    [candleBars, candleOpen],
  );

  if (loading) {
    return (
      <div
        className={cn("ds-universe-chart ds-universe-chart--empty", className)}
        role="status"
      >
        <span>Loading {timeframeLabel}</span>
      </div>
    );
  }

  if (chartType === "candles") {
    if (!candleBars || candleBars.length < 2) {
      return (
        <div
          className={cn("ds-universe-chart ds-universe-chart--empty", className)}
          role="img"
          aria-label={`${symbol} chart unavailable`}
        >
          <span>No {timeframeLabel} series</span>
        </div>
      );
    }

    const first = candleBars[0].close;
    const last = candleBars[candleBars.length - 1].close;
    const up = last >= first;

    return (
      <div
        className={cn(
          "ds-universe-chart ds-universe-chart--candles",
          peek && "is-peeking",
          className,
        )}
        role="img"
        aria-label={`${symbol} ${timeframeLabel} candles, ${candleBars.length} bars`}
      >
        <MiniCandles
          symbol={symbol}
          bars={candleBars}
          timeframeLabel={timeframeLabel}
          hoverIndex={candleHover}
          onHoverIndex={onCandleHover}
        />
        {peek ? (
          <ChartPeek peek={peek} timeframeLabel={timeframeLabel} detailed />
        ) : null}
        <span className="sr-only">{up ? "Up over window" : "Down over window"}</span>
      </div>
    );
  }

  if (data.length < 2) {
    return (
      <div
        className={cn("ds-universe-chart ds-universe-chart--empty", className)}
        role="img"
        aria-label={`${symbol} chart unavailable`}
      >
        <span>No {timeframeLabel} series</span>
      </div>
    );
  }

  const first = data[0].close;
  const last = data[data.length - 1].close;
  const up = last >= first;

  return (
    <div
      className={cn("ds-universe-chart", peek && "is-peeking", className)}
      style={{ ["--ds-chart-tone" as string]: tone }}
      role="img"
      aria-label={`${symbol} ${timeframeLabel} close series, ${data.length} bars`}
    >
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={data}
          margin={{ top: 4, right: 0, left: 0, bottom: 0 }}
          onMouseMove={onLineMove}
          onMouseLeave={() => setPeek(null)}
        >
          <defs>
            <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={tone} stopOpacity={0.35} />
              <stop offset="100%" stopColor={tone} stopOpacity={0} />
            </linearGradient>
          </defs>
          <YAxis domain={["dataMin", "dataMax"]} hide width={0} />
          <Tooltip
            cursor={{
              stroke: "color-mix(in srgb, var(--ds-chart-tone, var(--ds-signal)) 55%, var(--ds-line-strong))",
              strokeWidth: 1,
              strokeDasharray: "2 3",
            }}
            content={() => null}
            isAnimationActive={false}
          />
          <Area
            type="monotone"
            dataKey="close"
            stroke={tone}
            strokeWidth={1.5}
            fill={`url(#${gradId})`}
            isAnimationActive={false}
            dot={false}
            activeDot={{
              r: 3.5,
              fill: tone,
              stroke: "var(--ds-canvas)",
              strokeWidth: 1.5,
            }}
          />
        </AreaChart>
      </ResponsiveContainer>
      {peek ? <ChartPeek peek={peek} timeframeLabel={timeframeLabel} /> : null}
      <span className="sr-only">{up ? "Up over window" : "Down over window"}</span>
    </div>
  );
}
