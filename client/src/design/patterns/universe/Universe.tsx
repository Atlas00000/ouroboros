"use client";

import { useCallback, useMemo, useState } from "react";

import { EmptyState, ErrorState, LoadingState } from "@/components/ui/PageState";
import { StaleBadge } from "@/components/StaleBadge";
import { PageEnter } from "@/design/motion/PageEnter";
import { HOME_COPY } from "@/design/patterns/home-copy";
import { SectionWrap } from "@/design/patterns/SectionWrap";
import { UniverseAtmosphere } from "@/design/patterns/universe/UniverseAtmosphere";
import { UniverseChartTypeControl } from "@/design/patterns/universe/UniverseChartType";
import { UniverseFocus } from "@/design/patterns/universe/UniverseFocus";
import {
  UniverseFilter,
  type UniverseFilterKey,
} from "@/design/patterns/universe/UniverseFilter";
import { UniverseInstrument } from "@/design/patterns/universe/UniverseInstrument";
import { UniverseTimeframe } from "@/design/patterns/universe/UniverseTimeframe";
import {
  UNIVERSE_CHART_DEFAULT,
  UNIVERSE_CHART_LABEL,
  UNIVERSE_SPARK_DEFAULT,
  UNIVERSE_SPARK_LABEL,
  type UniverseChartType,
  type UniverseSparkTimeframe,
} from "@/design/patterns/universe/spark";
import type { DashboardCard } from "@/lib/queries/dashboard";

import "./universe.css";

export type UniverseProps = {
  cards: DashboardCard[];
  listStale?: boolean;
  generatedAt?: string;
  loading?: boolean;
  error?: string | null;
};

function countByFilter(cards: DashboardCard[]): Record<UniverseFilterKey, number> {
  const counts: Record<UniverseFilterKey, number> = {
    all: cards.length,
    trending_up: 0,
    trending_down: 0,
    ranging: 0,
    high_volatility: 0,
  };
  for (const c of cards) {
    const r = c.regime;
    if (r === "trending_up") counts.trending_up += 1;
    else if (r === "trending_down") counts.trending_down += 1;
    else if (r === "ranging") counts.ranging += 1;
    else if (r === "high_volatility") counts.high_volatility += 1;
  }
  return counts;
}

/**
 * Universe — professional instrument grid for Home.
 * Line / candle price series + regime / timeframe / chart-type controls.
 */
export function Universe({
  cards,
  listStale,
  generatedAt,
  loading,
  error,
}: UniverseProps) {
  const [filter, setFilter] = useState<UniverseFilterKey>("all");
  const [timeframe, setTimeframe] =
    useState<UniverseSparkTimeframe>(UNIVERSE_SPARK_DEFAULT);
  const [chartType, setChartType] =
    useState<UniverseChartType>(UNIVERSE_CHART_DEFAULT);
  const [hotSymbol, setHotSymbol] = useState<string | null>(null);
  const [focusSymbol, setFocusSymbol] = useState<string | null>(null);
  const closeFocus = useCallback(() => setFocusSymbol(null), []);

  const counts = useMemo(() => countByFilter(cards), [cards]);

  const visible = useMemo(() => {
    if (filter === "all") return cards;
    return cards.filter((c) => c.regime === filter);
  }, [cards, filter]);

  const focusedCard = useMemo(
    () => (focusSymbol ? cards.find((c) => c.asset.symbol === focusSymbol) ?? null : null),
    [cards, focusSymbol],
  );

  const focusRegime =
    filter !== "all"
      ? filter
      : (cards.find((c) => c.asset.symbol === hotSymbol)?.regime ?? null);

  if (loading) {
    return (
      <section className="ds-universe" aria-label="Universe">
        <LoadingState>Loading universe…</LoadingState>
      </section>
    );
  }

  if (error) {
    return (
      <section className="ds-universe" aria-label="Universe">
        <ErrorState title="Could not load universe">{error}</ErrorState>
      </section>
    );
  }

  if (!cards.length) {
    return (
      <section className="ds-universe" aria-label="Universe">
        <EmptyState title="No assets yet">
          Start Docker + API and set{" "}
          <code className="font-mono text-ds-ink">OUROBOROS_SERVER_API_KEY</code> for local SSR, or
          sign in with Clerk.
        </EmptyState>
      </section>
    );
  }

  return (
    <PageEnter>
      <section
        className="ds-universe"
        aria-label="Universe"
        data-filter={filter}
        data-timeframe={timeframe}
        data-chart={chartType}
      >
        <UniverseAtmosphere focusRegime={focusRegime} />

        <header className="ds-universe__header">
          <div>
            <h2 className="ds-universe__title">Universe</h2>
            <SectionWrap className="ds-universe__wrap">
              {HOME_COPY.universe.wrap}
            </SectionWrap>
            <div className="ds-universe__meta">
              <span className="ds-universe__as-of">
                {HOME_COPY.universe.eyebrow} · {UNIVERSE_SPARK_LABEL[timeframe]} ·{" "}
                {UNIVERSE_CHART_LABEL[chartType]}
              </span>
              <StaleBadge stale={listStale} />
              {generatedAt ? (
                <span className="ds-universe__as-of">as of {generatedAt}</span>
              ) : null}
              <span className="ds-universe__as-of">
                {visible.length} of {cards.length} on board
              </span>
            </div>
          </div>
          <div className="ds-universe__controls">
            <UniverseTimeframe value={timeframe} onChange={setTimeframe} />
            <UniverseChartTypeControl value={chartType} onChange={setChartType} />
            <UniverseFilter value={filter} counts={counts} onChange={setFilter} />
          </div>
        </header>

        {visible.length === 0 ? (
          <p className="ds-universe__empty-filter" role="status">
            No instruments in this regime cut. Choose another focus.
          </p>
        ) : (
          <ul className="ds-universe__grid">
            {visible.map((card) => (
              <UniverseInstrument
                key={`${card.asset.symbol}-${timeframe}`}
                card={card}
                timeframe={timeframe}
                chartType={chartType}
                active={hotSymbol === card.asset.symbol}
                onOpen={() => setFocusSymbol(card.asset.symbol)}
                onFocus={() => setHotSymbol(card.asset.symbol)}
                onBlur={() =>
                  setHotSymbol((cur) => (cur === card.asset.symbol ? null : cur))
                }
              />
            ))}
          </ul>
        )}

        {focusedCard ? (
          <UniverseFocus
            card={focusedCard}
            timeframe={timeframe}
            chartType={chartType}
            onClose={closeFocus}
          />
        ) : null}
      </section>
    </PageEnter>
  );
}
