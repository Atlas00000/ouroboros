"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import {
  impactLabel,
  impactToneVar,
  normalizeImpact,
} from "@/design/patterns/news-ticker/TickerImpact";
import type { NewsListItem } from "@/lib/api/types";

type TickerLeadProps = {
  item: NewsListItem | null;
  index: number;
  total: number;
};

/** Living lead story — large type that crossfades with the stream. */
export function TickerLead({ item, index, total }: TickerLeadProps) {
  const [tick, setTick] = useState(0);

  useEffect(() => {
    if (!item) return;
    setTick((n) => n + 1);
  }, [item?.id]);

  if (!item) {
    return (
      <div className="ds-ticker-lead" data-empty="true">
        <p className="ds-ticker-lead__hint">Tape quiet — awaiting headlines.</p>
      </div>
    );
  }

  const level = normalizeImpact(item.impact);
  const href = item.url || (item.symbol ? `/assets/${item.symbol}` : "/news");
  const external = Boolean(item.url);

  return (
    <div
      className="ds-ticker-lead"
      data-level={level}
      style={{ ["--ds-ticker-impact" as string]: impactToneVar(level) }}
      aria-live="polite"
    >
      <div className="ds-ticker-lead__meta">
        <span className="ds-ticker-lead__index">
          {String(index + 1).padStart(2, "0")}
          <span className="ds-ticker-lead__of">/{String(total).padStart(2, "0")}</span>
        </span>
        <span className="ds-ticker-lead__impact">{impactLabel(level)}</span>
      </div>

      <p key={tick} className="ds-ticker-lead__headline">
        {item.headline}
      </p>

      <div className="ds-ticker-lead__foot">
        <span>{item.source}</span>
        {item.symbol ? (
          <>
            <span aria-hidden>·</span>
            <Link href={`/assets/${item.symbol}`} className="ds-ticker-lead__sym">
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
          className="ds-ticker-lead__cta"
        >
          Open release →
        </a>
      ) : (
        <Link href={href} className="ds-ticker-lead__cta">
          {item.symbol ? `Open ${item.symbol} →` : "Open news desk →"}
        </Link>
      )}
    </div>
  );
}
