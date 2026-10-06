"use client";

import Link from "next/link";
import type { CSSProperties } from "react";

import { StateBadge } from "@/components/StateBadge";
import { NumberTick } from "@/design/motion/NumberTick";
import { cssVarForTone, REGIME_LABEL, toneForRegime } from "@/design/map/backend-visual";
import type { DashboardCard } from "@/lib/queries/dashboard";

type HeroRegimeStageProps = {
  cards: DashboardCard[];
};

const KEYS = ["trending_up", "trending_down", "ranging", "high_volatility"] as const;

function countMix(cards: DashboardCard[]) {
  const mix = {
    trending_up: 0,
    trending_down: 0,
    ranging: 0,
    high_volatility: 0,
  };
  for (const c of cards) {
    const r = c.regime;
    if (r === "trending_up") mix.trending_up += 1;
    else if (r === "trending_down") mix.trending_down += 1;
    else if (r === "ranging") mix.ranging += 1;
    else if (r === "high_volatility") mix.high_volatility += 1;
  }
  return mix;
}

/** Regime desk — structure counts + featured instruments (no bar chrome). */
export function HeroRegimeStage({ cards }: HeroRegimeStageProps) {
  const mix = countMix(cards);
  const featured = cards.slice(0, 6);

  return (
    <div className="ds-hero-stage ds-hero-stage--regimes">
      <div className="ds-hero-stage__lead">
        <p className="ds-hero-stage__kicker">Watchlist structure</p>
        <p className="ds-hero-stage__stat">
          <NumberTick value={cards.length} />
          <span>instruments under watch</span>
        </p>
      </div>

      <ul className="ds-hero-regime__mix" aria-label="Regime mix">
        {KEYS.map((key) => (
          <li
            key={key}
            className="ds-hero-regime__stat"
            style={
              {
                ["--ds-band-tone" as string]: cssVarForTone(toneForRegime(key)),
              } as CSSProperties
            }
          >
            <span className="ds-hero-regime__label">{REGIME_LABEL[key]}</span>
            <span className="ds-hero-regime__n">{mix[key]}</span>
          </li>
        ))}
      </ul>

      <ul className="ds-hero-regime__list">
        {featured.map((c) => (
          <li key={c.asset.symbol}>
            <Link
              href={`/assets/${c.asset.symbol}`}
              className="ds-hero-regime__row"
            >
              <span className="ds-hero-regime__sym">{c.asset.symbol}</span>
              <span className="ds-hero-regime__name">{c.asset.display_name}</span>
              <StateBadge regime={c.regime} />
            </Link>
          </li>
        ))}
        {!featured.length ? (
          <li className="ds-hero-stage__empty">No assets on the desk yet.</li>
        ) : null}
      </ul>
    </div>
  );
}
