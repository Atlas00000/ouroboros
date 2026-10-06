"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import {
  impactToneVar,
  normalizeImpact,
} from "@/design/patterns/news-ticker/TickerImpact";
import { HOME_COPY } from "@/design/patterns/home-copy";
import { SectionWrap } from "@/design/patterns/SectionWrap";
import type { NewsListItem } from "@/lib/api/types";

type HeroTapeProps = {
  items: NewsListItem[];
  paused?: boolean;
};

const STEP_MS = 3200;

/**
 * Live tape — steps through real headlines continuously.
 */
export function HeroTape({ items, paused }: HeroTapeProps) {
  const cut = items.slice(0, 12);
  const [index, setIndex] = useState(0);
  const [reduceMotion, setReduceMotion] = useState(false);

  useEffect(() => {
    setReduceMotion(window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  }, []);

  useEffect(() => {
    if (paused || reduceMotion || cut.length < 2) return;
    const id = window.setInterval(() => {
      setIndex((i) => (i + 1) % cut.length);
    }, STEP_MS);
    return () => window.clearInterval(id);
  }, [paused, reduceMotion, cut.length]);

  if (!cut.length) return null;

  const windowed = [
    cut[index % cut.length],
    cut[(index + 1) % cut.length],
    cut[(index + 2) % cut.length],
  ].filter(Boolean);

  return (
    <div className="ds-hero-tape" aria-label="Live headline tape">
      <div className="ds-hero-tape__intro">
        <span className="ds-hero-tape__live">
          <span className="ds-hero-tape__dot" aria-hidden />
          {HOME_COPY.tape.kicker}
        </span>
        <SectionWrap className="ds-section-wrap--lane ds-hero-tape__wrap">
          {HOME_COPY.tape.wrap}
        </SectionWrap>
      </div>
      <ul className="ds-hero-tape__list">
        {windowed.map((item, i) => {
          const level = normalizeImpact(item.impact);
          return (
            <li
              key={`${item.id}-${i}`}
              className="ds-hero-tape__item"
              style={{ ["--ds-tape-tone" as string]: impactToneVar(level) }}
              data-lead={i === 0 ? "true" : "false"}
            >
              {item.symbol ? (
                <Link href={`/assets/${item.symbol}`} className="ds-hero-tape__sym">
                  {item.symbol}
                </Link>
              ) : (
                <span className="ds-hero-tape__sym is-muted">{item.source}</span>
              )}
              <span className="ds-hero-tape__text">{item.headline}</span>
            </li>
          );
        })}
      </ul>
      <Link href="/news" className="ds-hero-tape__more">
        Full desk →
      </Link>
    </div>
  );
}
