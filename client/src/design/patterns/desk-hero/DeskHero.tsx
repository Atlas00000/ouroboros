"use client";

import { useCallback, useState } from "react";

import { StaleBadge } from "@/components/StaleBadge";
import { PageEnter } from "@/design/motion/PageEnter";
import { NumberTick } from "@/design/motion/NumberTick";
import { DeskHeroAtmosphere } from "@/design/patterns/desk-hero/DeskHeroAtmosphere";
import { HeroFeaturedPrice } from "@/design/patterns/desk-hero/HeroFeaturedPrice";
import { HeroPressLane } from "@/design/patterns/desk-hero/HeroPressLane";
import { HeroSparkStrip } from "@/design/patterns/desk-hero/HeroSparkStrip";
import { HeroTape } from "@/design/patterns/desk-hero/HeroTape";
import { useHeroSparks } from "@/design/patterns/desk-hero/useHeroSparks";
import { FitHeroChip } from "@/design/patterns/fit/FitHeroChip";
import { HOME_COPY } from "@/design/patterns/home-copy";
import { SectionWrap } from "@/design/patterns/SectionWrap";
import type { NewsListItem } from "@/lib/api/types";
import type { DashboardCard } from "@/lib/queries/dashboard";

import "./desk-hero.css";

export type DeskHeroProps = {
  cards: DashboardCard[];
  newsItems?: NewsListItem[];
  stale?: boolean;
  generatedAt?: string;
};

/**
 * Living desk hero — mosaic of price action, press, sparks, and tape.
 * Always on; pauses cycling while hovered / focused.
 */
export function DeskHero({
  cards,
  newsItems = [],
  stale,
  generatedAt,
}: DeskHeroProps) {
  const [paused, setPaused] = useState(false);
  const [activeSymbol, setActiveSymbol] = useState<string | null>(null);
  const [lockedSymbol, setLockedSymbol] = useState<string | null>(null);
  const bundles = useHeroSparks(cards, 5);

  const highImpact = newsItems.filter((n) => {
    const s = (n.impact ?? "").toLowerCase();
    return s === "high" || s === "critical" || s === "severe";
  }).length;

  const onSelectFromStrip = useCallback((symbol: string) => {
    setLockedSymbol(symbol);
    setActiveSymbol(symbol);
  }, []);

  return (
    <PageEnter>
      <section
        className="ds-desk-hero"
        aria-label="Ouroboros desk hero"
        data-stage="mosaic"
        onPointerEnter={() => setPaused(true)}
        onPointerLeave={() => {
          setPaused(false);
          setLockedSymbol(null);
        }}
        onFocusCapture={() => setPaused(true)}
        onBlurCapture={(e) => {
          if (!e.currentTarget.contains(e.relatedTarget as Node | null)) {
            setPaused(false);
            setLockedSymbol(null);
          }
        }}
      >
        <DeskHeroAtmosphere stage="pricing" />

        <div className="ds-desk-hero__content">
          <header className="ds-desk-hero__mast">
            <div className="ds-desk-hero__brand">
              <p className="ds-desk-hero__eyebrow">
                {HOME_COPY.hero.eyebrow}
                <StaleBadge stale={stale} />
                <FitHeroChip symbol={activeSymbol ?? lockedSymbol} />
              </p>
              <h1 className="ds-desk-hero__title">Ouroboros</h1>
              <SectionWrap className="ds-desk-hero__wrap">
                {HOME_COPY.hero.wrap}
              </SectionWrap>
              {generatedAt ? (
                <p className="ds-desk-hero__asof">as of {generatedAt}</p>
              ) : null}
            </div>

            <div className="ds-desk-hero__vitals" aria-label="Desk vitals">
              <div className="ds-desk-hero__vital">
                <span className="ds-desk-hero__vital-label">Universe</span>
                <span className="ds-desk-hero__vital-value">
                  <NumberTick value={cards.length} />
                </span>
              </div>
              <div className="ds-desk-hero__vital">
                <span className="ds-desk-hero__vital-label">High impact</span>
                <span className="ds-desk-hero__vital-value">
                  <NumberTick value={highImpact || newsItems.length} />
                </span>
              </div>
              <div className="ds-desk-hero__vital">
                <span className="ds-desk-hero__vital-label">On path</span>
                <span className="ds-desk-hero__vital-value">
                  <NumberTick value={bundles.length} />
                </span>
              </div>
            </div>
          </header>

          <div className="ds-desk-hero__mosaic">
            <HeroFeaturedPrice
              bundles={bundles}
              paused={paused}
              lockedSymbol={lockedSymbol}
              onActiveSymbol={setActiveSymbol}
            />
            <HeroPressLane items={newsItems} paused={paused} />
          </div>

          <HeroSparkStrip
            bundles={bundles}
            activeSymbol={activeSymbol ?? undefined}
            onSelectSymbol={onSelectFromStrip}
          />

          <HeroTape items={newsItems} paused={paused} />
        </div>
      </section>
    </PageEnter>
  );
}
