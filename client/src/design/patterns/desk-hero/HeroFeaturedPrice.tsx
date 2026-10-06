"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import { StateBadge } from "@/components/StateBadge";
import { UniverseMiniChart } from "@/design/patterns/universe/UniverseMiniChart";
import {
  chgTone,
  formatHeroChg,
  formatHeroPx,
  type HeroSparkBundle,
} from "@/design/patterns/desk-hero/useHeroSparks";
import { HOME_COPY } from "@/design/patterns/home-copy";
import { SectionWrap } from "@/design/patterns/SectionWrap";
import { cn } from "@/lib/utils";

type HeroFeaturedPriceProps = {
  bundles: HeroSparkBundle[];
  paused?: boolean;
  /** Sync featured symbol when strip is clicked. */
  lockedSymbol?: string | null;
  onActiveSymbol?: (symbol: string) => void;
};

const CYCLE_MS = 5500;

/**
 * Featured price path — cycles real M15 series across hot instruments.
 */
export function HeroFeaturedPrice({
  bundles,
  paused,
  lockedSymbol,
  onActiveSymbol,
}: HeroFeaturedPriceProps) {
  const [index, setIndex] = useState(0);
  const [reduceMotion, setReduceMotion] = useState(false);

  useEffect(() => {
    setReduceMotion(window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  }, []);

  useEffect(() => {
    if (!lockedSymbol || !bundles.length) return;
    const i = bundles.findIndex((b) => b.card.asset.symbol === lockedSymbol);
    if (i >= 0) setIndex(i);
  }, [lockedSymbol, bundles]);

  useEffect(() => {
    if (paused || reduceMotion || lockedSymbol || bundles.length < 2) return;
    const id = window.setInterval(() => {
      setIndex((i) => (i + 1) % bundles.length);
    }, CYCLE_MS);
    return () => window.clearInterval(id);
  }, [paused, reduceMotion, lockedSymbol, bundles.length]);

  useEffect(() => {
    const sym = bundles[index]?.card.asset.symbol;
    if (sym) onActiveSymbol?.(sym);
  }, [index, bundles, onActiveSymbol]);

  const active = bundles[index] ?? bundles[0];
  if (!active) {
    return (
      <div className="ds-hero-featured">
        <p className="ds-hero-stage__empty">No price paths on the desk yet.</p>
      </div>
    );
  }

  const { card, series, loading } = active;
  const last = series?.lastClose ?? null;
  const chg = series?.changePct ?? null;

  return (
    <div className="ds-hero-featured" data-tone={chgTone(chg)}>
      <div className="ds-hero-featured__head">
        <div>
          <p className="ds-hero-featured__kicker">{HOME_COPY.featured.kicker}</p>
          <Link
            href={`/assets/${card.asset.symbol}`}
            className="ds-hero-featured__sym"
          >
            {card.asset.symbol}
          </Link>
          <p className="ds-hero-featured__name">{card.asset.display_name}</p>
          <SectionWrap className="ds-section-wrap--lane ds-hero-featured__wrap">
            {HOME_COPY.featured.wrap}
          </SectionWrap>
        </div>
        <div className="ds-hero-featured__metrics">
          <StateBadge regime={card.regime} />
          <span className="ds-hero-featured__last">{formatHeroPx(last)}</span>
          <span className="ds-hero-featured__chg" data-tone={chgTone(chg)}>
            {formatHeroChg(chg)}
          </span>
        </div>
      </div>

      <UniverseMiniChart
        symbol={card.asset.symbol}
        closes={series?.closes}
        bars={series?.bars}
        chartType="line"
        regime={card.regime}
        loading={loading}
        timeframeLabel="15m"
        className="ds-hero-featured__chart"
      />

      {bundles.length > 1 ? (
        <div className="ds-hero-featured__dots" role="tablist" aria-label="Featured instruments">
          {bundles.map((b, i) => (
            <button
              key={b.card.asset.symbol}
              type="button"
              role="tab"
              aria-selected={i === index}
              className={cn("ds-hero-featured__dot", i === index && "is-active")}
              onClick={() => setIndex(i)}
            >
              {b.card.asset.symbol}
            </button>
          ))}
        </div>
      ) : null}
    </div>
  );
}
