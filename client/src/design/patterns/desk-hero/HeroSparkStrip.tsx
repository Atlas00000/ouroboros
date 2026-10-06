"use client";

import Link from "next/link";

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

type HeroSparkStripProps = {
  bundles: HeroSparkBundle[];
  activeSymbol?: string;
  onSelectSymbol?: (symbol: string) => void;
};

/** Always-on mini price strip — real series only. */
export function HeroSparkStrip({
  bundles,
  activeSymbol,
  onSelectSymbol,
}: HeroSparkStripProps) {
  if (!bundles.length) return null;

  return (
    <div className="ds-hero-strip">
      <div className="ds-hero-strip__intro">
        <p className="ds-hero-strip__kicker">{HOME_COPY.strip.kicker}</p>
        <SectionWrap className="ds-section-wrap--lane">
          {HOME_COPY.strip.wrap}
        </SectionWrap>
      </div>
      <ul className="ds-hero-strip__row">
        {bundles.map(({ card, series, loading }) => {
          const chg = series?.changePct ?? null;
          const active = activeSymbol === card.asset.symbol;
          return (
            <li key={card.asset.symbol}>
              <button
                type="button"
                className={cn("ds-hero-strip__tile", active && "is-active")}
                onClick={() => onSelectSymbol?.(card.asset.symbol)}
              >
                <span className="ds-hero-strip__sym">{card.asset.symbol}</span>
                <UniverseMiniChart
                  symbol={card.asset.symbol}
                  closes={series?.closes}
                  bars={series?.bars}
                  chartType="line"
                  regime={card.regime}
                  loading={loading}
                  timeframeLabel="15m"
                  className="ds-hero-strip__chart"
                />
                <span className="ds-hero-strip__foot">
                  <span>{formatHeroPx(series?.lastClose)}</span>
                  <span data-tone={chgTone(chg)}>{formatHeroChg(chg)}</span>
                </span>
              </button>
              <Link
                href={`/assets/${card.asset.symbol}`}
                className="ds-hero-strip__link"
              >
                Open
              </Link>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
