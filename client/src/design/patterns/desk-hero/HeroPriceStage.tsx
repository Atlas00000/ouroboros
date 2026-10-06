"use client";

import { useQueries } from "@tanstack/react-query";
import Link from "next/link";

import { StateBadge } from "@/components/StateBadge";
import { UniverseMiniChart } from "@/design/patterns/universe/UniverseMiniChart";
import type { UniverseSparkSeries } from "@/design/patterns/universe/spark";
import type { DashboardCard } from "@/lib/queries/dashboard";

type HeroPriceStageProps = {
  cards: DashboardCard[];
};

function pickPriced(cards: DashboardCard[], limit = 4): DashboardCard[] {
  const ranked = [...cards].sort((a, b) => {
    const av = a.volPercentile ?? -1;
    const bv = b.volPercentile ?? -1;
    return bv - av;
  });
  return ranked.slice(0, Math.min(limit, ranked.length));
}

/** Pricing desk — real M15 paths for featured instruments. */
export function HeroPriceStage({ cards }: HeroPriceStageProps) {
  const featured = pickPriced(cards, 4);

  const queries = useQueries({
    queries: featured.map((card) => ({
      queryKey: ["desk-hero-spark", "M15", card.asset.symbol],
      staleTime: 60_000,
      queryFn: async (): Promise<UniverseSparkSeries> => {
        const params = new URLSearchParams({
          symbol: card.asset.symbol,
          timeframe: "M15",
        });
        const res = await fetch(`/api/universe-spark?${params}`, {
          cache: "no-store",
        });
        if (!res.ok) throw new Error(`spark ${res.status}`);
        return (await res.json()) as UniverseSparkSeries;
      },
    })),
  });

  return (
    <div className="ds-hero-stage ds-hero-stage--pricing">
      <div className="ds-hero-stage__lead">
        <p className="ds-hero-stage__kicker">15m close paths</p>
        <p className="ds-hero-stage__lede">
          Featured by realized-vol posture — chart honesty, not prediction.
        </p>
      </div>

      {!featured.length ? (
        <p className="ds-hero-stage__empty">No priced instruments available.</p>
      ) : (
        <ul className="ds-hero-price__grid">
          {featured.map((card, i) => {
            const q = queries[i];
            const series = q?.data;
            const loading = Boolean(q?.isLoading || q?.isFetching);
            const last = series?.lastClose ?? null;
            const chg = series?.changePct ?? null;
            const tone =
              chg == null ? "flat" : chg > 0 ? "up" : chg < 0 ? "down" : "flat";

            return (
              <li key={card.asset.symbol}>
                <Link
                  href={`/assets/${card.asset.symbol}`}
                  className="ds-hero-price__tile"
                >
                  <header className="ds-hero-price__head">
                    <span className="ds-hero-price__sym">{card.asset.symbol}</span>
                    <StateBadge regime={card.regime} />
                  </header>
                  <UniverseMiniChart
                    symbol={card.asset.symbol}
                    closes={series?.closes}
                    bars={series?.bars}
                    chartType="line"
                    regime={card.regime}
                    loading={loading}
                    timeframeLabel="15m"
                    className="ds-hero-price__chart"
                  />
                  <footer className="ds-hero-price__foot">
                    <span className="ds-hero-price__last">
                      {last == null
                        ? "—"
                        : Math.abs(last) >= 1
                          ? last.toFixed(4)
                          : last.toPrecision(5)}
                    </span>
                    <span className="ds-hero-price__chg" data-tone={tone}>
                      {chg == null
                        ? "—"
                        : `${chg > 0 ? "+" : ""}${chg.toFixed(2)}%`}
                    </span>
                  </footer>
                </Link>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
