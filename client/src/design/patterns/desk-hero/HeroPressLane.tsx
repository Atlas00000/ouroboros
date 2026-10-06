"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import {
  impactLabel,
  impactToneVar,
  normalizeImpact,
} from "@/design/patterns/news-ticker/TickerImpact";
import { HOME_COPY } from "@/design/patterns/home-copy";
import { SectionWrap } from "@/design/patterns/SectionWrap";
import type { NewsListItem } from "@/lib/api/types";
import { cn } from "@/lib/utils";

type HeroPressLaneProps = {
  items: NewsListItem[];
  paused?: boolean;
};

const CYCLE_MS = 4200;

/**
 * Press / release lane — cycles real headlines (with source url when present).
 */
export function HeroPressLane({ items, paused }: HeroPressLaneProps) {
  const cut = items.slice(0, 8);
  const [index, setIndex] = useState(0);
  const [reduceMotion, setReduceMotion] = useState(false);

  useEffect(() => {
    setReduceMotion(window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  }, []);

  useEffect(() => {
    if (paused || reduceMotion || cut.length < 2) return;
    const id = window.setInterval(() => {
      setIndex((i) => (i + 1) % cut.length);
    }, CYCLE_MS);
    return () => window.clearInterval(id);
  }, [paused, reduceMotion, cut.length]);

  const item = cut[index] ?? cut[0];
  if (!item) {
    return (
      <div className="ds-hero-press">
        <p className="ds-hero-stage__empty">No press or headlines in the current cut.</p>
      </div>
    );
  }

  const level = normalizeImpact(item.impact);
  const href = item.url || (item.symbol ? `/assets/${item.symbol}` : "/news");
  const external = Boolean(item.url);

  return (
    <div
      className="ds-hero-press"
      style={{ ["--ds-press-tone" as string]: impactToneVar(level) }}
    >
      <div className="ds-hero-press__head">
        <div>
          <p className="ds-hero-press__kicker">{HOME_COPY.press.kicker}</p>
          <SectionWrap className="ds-section-wrap--lane">
            {HOME_COPY.press.wrap}
          </SectionWrap>
        </div>
        <span className="ds-hero-press__impact">{impactLabel(level)}</span>
      </div>

      <p key={item.id} className="ds-hero-press__headline">
        {item.headline}
      </p>

      <div className="ds-hero-press__meta">
        <span>{item.source}</span>
        {item.symbol ? (
          <>
            <span aria-hidden>·</span>
            <Link href={`/assets/${item.symbol}`} className="ds-hero-press__sym">
              {item.symbol}
            </Link>
          </>
        ) : null}
        {item.published_at ? (
          <>
            <span aria-hidden>·</span>
            <span>{item.published_at.slice(0, 16)}</span>
          </>
        ) : null}
      </div>

      {external ? (
        <a
          href={href}
          target="_blank"
          rel="noopener noreferrer"
          className="ds-hero-press__cta"
        >
          Open release →
        </a>
      ) : (
        <Link href={href} className="ds-hero-press__cta">
          {item.symbol ? `Open ${item.symbol} →` : "Open news desk →"}
        </Link>
      )}

      {cut.length > 1 ? (
        <div className="ds-hero-press__rail" aria-hidden>
          {cut.map((n, i) => (
            <button
              key={n.id}
              type="button"
              className={cn("ds-hero-press__tick", i === index && "is-active")}
              onClick={() => setIndex(i)}
              aria-label={`Show headline ${i + 1}`}
            />
          ))}
        </div>
      ) : null}
    </div>
  );
}
