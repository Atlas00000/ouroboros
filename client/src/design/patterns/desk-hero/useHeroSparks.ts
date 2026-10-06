"use client";

import { useQueries } from "@tanstack/react-query";
import { useMemo } from "react";

import type { UniverseSparkSeries } from "@/design/patterns/universe/spark";
import type { DashboardCard } from "@/lib/queries/dashboard";

export type HeroSparkBundle = {
  card: DashboardCard;
  series: UniverseSparkSeries | undefined;
  loading: boolean;
};

function rankCards(cards: DashboardCard[], limit: number): DashboardCard[] {
  return [...cards]
    .sort((a, b) => (b.volPercentile ?? -1) - (a.volPercentile ?? -1))
    .slice(0, Math.min(limit, cards.length));
}

/** Shared M15 spark fetch for hero mosaic lanes. */
export function useHeroSparks(cards: DashboardCard[], limit = 5): HeroSparkBundle[] {
  const featured = useMemo(() => rankCards(cards, limit), [cards, limit]);

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

  return featured.map((card, i) => ({
    card,
    series: queries[i]?.data,
    loading: Boolean(queries[i]?.isLoading || queries[i]?.isFetching),
  }));
}

export function formatHeroPx(n: number | null | undefined): string {
  if (n == null || Number.isNaN(n)) return "—";
  if (Math.abs(n) >= 1000) return n.toFixed(1);
  if (Math.abs(n) >= 1) return n.toFixed(4);
  return n.toPrecision(5);
}

export function formatHeroChg(pct: number | null | undefined): string {
  if (pct == null || Number.isNaN(pct)) return "—";
  return `${pct > 0 ? "+" : ""}${pct.toFixed(2)}%`;
}

export function chgTone(pct: number | null | undefined): "up" | "down" | "flat" {
  if (pct == null || Number.isNaN(pct) || pct === 0) return "flat";
  return pct > 0 ? "up" : "down";
}
