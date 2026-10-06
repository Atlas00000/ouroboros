"use client";

import { useQuery } from "@tanstack/react-query";

import { StateBadge } from "@/components/StateBadge";
import { StaleBadge } from "@/components/StaleBadge";
import { cssVarForTone, toneForRegime, type Regime } from "@/design/map/backend-visual";
import { UniverseMiniChart } from "@/design/patterns/universe/UniverseMiniChart";
import { UniverseSentiment } from "@/design/patterns/universe/UniverseSentiment";
import { UniverseVolGauge } from "@/design/patterns/universe/UniverseVolGauge";
import {
  UNIVERSE_CHART_DEFAULT,
  UNIVERSE_SPARK_DEFAULT,
  UNIVERSE_SPARK_LABEL,
  type UniverseChartType,
  type UniverseSparkSeries,
  type UniverseSparkTimeframe,
} from "@/design/patterns/universe/spark";
import type { DashboardCard } from "@/lib/queries/dashboard";
import { cn } from "@/lib/utils";

type UniverseInstrumentProps = {
  card: DashboardCard;
  timeframe?: UniverseSparkTimeframe;
  chartType?: UniverseChartType;
  active?: boolean;
  onOpen?: () => void;
  onFocus?: () => void;
  onBlur?: () => void;
};

function formatClose(n: number | null | undefined): string {
  if (n == null || Number.isNaN(n)) return "—";
  if (Math.abs(n) >= 1000) return n.toFixed(1);
  if (Math.abs(n) >= 1) return n.toFixed(4);
  return n.toPrecision(5);
}

function formatChange(pct: number | null | undefined): string {
  if (pct == null || Number.isNaN(pct)) return "—";
  const sign = pct > 0 ? "+" : "";
  return `${sign}${pct.toFixed(2)}%`;
}

function useInstrumentSeries(card: DashboardCard, timeframe: UniverseSparkTimeframe) {
  const q = useQuery({
    queryKey: ["universe-spark", timeframe, card.asset.symbol],
    staleTime: 60_000,
    queryFn: async (): Promise<UniverseSparkSeries> => {
      const params = new URLSearchParams({
        symbol: card.asset.symbol,
        timeframe,
      });
      const res = await fetch(`/api/universe-spark?${params}`, { cache: "no-store" });
      if (!res.ok) {
        throw new Error(`spark ${res.status}`);
      }
      return (await res.json()) as UniverseSparkSeries;
    },
  });

  return {
    closes: q.data?.closes ?? [],
    bars: q.data?.bars ?? [],
    lastClose: q.data?.lastClose ?? null,
    changePct: q.data?.changePct ?? null,
    loading: q.isLoading,
  };
}

/** Professional instrument tile for the Universe grid — opens desk focus. */
export function UniverseInstrument({
  card,
  timeframe = UNIVERSE_SPARK_DEFAULT,
  chartType = UNIVERSE_CHART_DEFAULT,
  active,
  onOpen,
  onFocus,
  onBlur,
}: UniverseInstrumentProps) {
  const { asset, regime, volPercentile, sentimentScore, stale } = card;
  const tone = cssVarForTone(toneForRegime(regime as Regime));
  const series = useInstrumentSeries(card, timeframe);
  const changeTone =
    series.changePct == null
      ? "flat"
      : series.changePct > 0
        ? "up"
        : series.changePct < 0
          ? "down"
          : "flat";

  return (
    <li
      className={cn("ds-universe-tile", active && "is-hot")}
      data-regime={regime ?? "unknown"}
      style={{ ["--ds-instrument-tone" as string]: tone }}
      onMouseEnter={onFocus}
      onMouseLeave={onBlur}
    >
      <button
        type="button"
        className="ds-universe-tile__link"
        aria-label={`Focus ${asset.symbol} ${asset.display_name}`}
        onClick={onOpen}
        onFocus={onFocus}
        onBlur={onBlur}
      >
        <header className="ds-universe-tile__head">
          <div className="ds-universe-tile__id">
            <div className="ds-universe-tile__symbol-row">
              <span className="ds-universe-tile__symbol">{asset.symbol}</span>
              <StaleBadge stale={stale} />
            </div>
            <span className="ds-universe-tile__name">{asset.display_name}</span>
          </div>
          <StateBadge regime={regime} />
        </header>

        <UniverseMiniChart
          symbol={asset.symbol}
          closes={series.closes}
          bars={series.bars}
          chartType={chartType}
          regime={regime}
          loading={series.loading}
          timeframeLabel={UNIVERSE_SPARK_LABEL[timeframe]}
          className="ds-universe-tile__chart"
        />

        <footer className="ds-universe-tile__foot">
          <div className="ds-universe-tile__px">
            <span className="ds-universe-tile__last">{formatClose(series.lastClose)}</span>
            <span className="ds-universe-tile__chg" data-tone={changeTone}>
              {formatChange(series.changePct)}
            </span>
          </div>
          <div className="ds-universe-tile__stats">
            <UniverseVolGauge value={volPercentile} />
            <UniverseSentiment score={sentimentScore} />
          </div>
        </footer>
      </button>
    </li>
  );
}
