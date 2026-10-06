"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { PageEnter } from "@/design/motion/PageEnter";
import { TickerAtmosphere } from "@/design/patterns/news-ticker/TickerAtmosphere";
import { countByImpact, type TickerFilterKey } from "@/design/patterns/news-ticker/TickerFilter";
import {
  impactToneVar,
  normalizeImpact,
} from "@/design/patterns/news-ticker/TickerImpact";
import { TickerLead } from "@/design/patterns/news-ticker/TickerLead";
import { TickerMast } from "@/design/patterns/news-ticker/TickerMast";
import { TickerPressure } from "@/design/patterns/news-ticker/TickerPressure";
import { TickerStream } from "@/design/patterns/news-ticker/TickerStream";
import type { NewsListItem } from "@/lib/api/types";

import "./news-ticker.css";

export type SignalTickerProps = {
  items: NewsListItem[];
  limit?: number;
};

const DWELL_MS = 4500;

/**
 * Drivers rail — living blend of rotating lead + depth stream.
 * Auto-advances; pauses on hover / focus. Soft pressure cut, no brick chrome.
 */
export function SignalTicker({ items, limit = 10 }: SignalTickerProps) {
  const stage = useMemo(() => items.slice(0, limit), [items, limit]);
  const [filter, setFilter] = useState<TickerFilterKey>("all");
  const [cursor, setCursor] = useState(0);
  const [paused, setPaused] = useState(false);
  const [manualId, setManualId] = useState<number | null>(null);

  const counts = useMemo(
    () => countByImpact(stage.map((n) => n.impact)),
    [stage],
  );

  const visible = useMemo(() => {
    if (filter === "all") return stage;
    return stage.filter((n) => normalizeImpact(n.impact) === filter);
  }, [stage, filter]);

  useEffect(() => {
    setCursor(0);
    setManualId(null);
  }, [filter]);

  useEffect(() => {
    if (paused || visible.length < 2) return;
    if (manualId != null) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    const id = window.setInterval(() => {
      setCursor((c) => (c + 1) % visible.length);
    }, DWELL_MS);
    return () => window.clearInterval(id);
  }, [paused, visible.length, manualId, visible]);

  const activeIndex = useMemo(() => {
    if (!visible.length) return -1;
    if (manualId != null) {
      const i = visible.findIndex((n) => n.id === manualId);
      if (i >= 0) return i;
    }
    return cursor % visible.length;
  }, [visible, cursor, manualId]);

  const active = activeIndex >= 0 ? visible[activeIndex] : null;
  const focusLevel = active ? normalizeImpact(active.impact) : "unknown";
  const focusTone = impactToneVar(focusLevel);

  const onActivate = (id: number) => {
    setManualId(id);
    const i = visible.findIndex((n) => n.id === id);
    if (i >= 0) setCursor(i);
  };

  if (!stage.length) {
    return (
      <section className="ds-ticker" aria-label="Drivers">
        <div className="ds-ticker__empty">
          <p className="ds-ticker__empty-title">Tape quiet</p>
          <p className="ds-ticker__empty-copy">No recent headlines on this desk.</p>
          <Link href="/news" className="ds-ticker-lead__cta">
            Open news desk →
          </Link>
        </div>
      </section>
    );
  }

  return (
    <PageEnter>
      <section
        className="ds-ticker"
        aria-label="Drivers"
        data-filter={filter}
        style={{ ["--ds-ticker-focus" as string]: focusTone }}
        onPointerEnter={() => setPaused(true)}
        onPointerLeave={() => {
          setPaused(false);
          setManualId(null);
        }}
        onFocusCapture={() => setPaused(true)}
        onBlurCapture={(e) => {
          if (!e.currentTarget.contains(e.relatedTarget as Node | null)) {
            setPaused(false);
            setManualId(null);
          }
        }}
      >
        <TickerAtmosphere
          focusLevel={focusLevel}
          focusSymbol={active?.symbol}
        />

        <div className="ds-ticker__content">
          <TickerMast count={stage.length} live={!paused} />
          <TickerLead
            item={active}
            index={Math.max(0, activeIndex)}
            total={visible.length}
          />
          <TickerPressure value={filter} counts={counts} onChange={setFilter} />
          <TickerStream
            items={visible}
            activeId={active?.id ?? null}
            onActivate={onActivate}
          />
        </div>
      </section>
    </PageEnter>
  );
}
