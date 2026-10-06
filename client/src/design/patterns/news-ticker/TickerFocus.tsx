"use client";

import Link from "next/link";

import {
  TickerImpact,
  impactLabel,
  normalizeImpact,
} from "@/design/patterns/news-ticker/TickerImpact";
import type { NewsListItem } from "@/lib/api/types";

type TickerFocusProps = {
  item: NewsListItem | null;
  index?: number;
};

/** Staged headline — large type plane, not a boxed preview card. */
export function TickerFocus({ item, index = 0 }: TickerFocusProps) {
  if (!item) {
    return (
      <div className="ds-ticker-focus" data-empty="true">
        <p className="ds-ticker-focus__hint">
          Stage a headline — hover or focus a row on the tape.
        </p>
      </div>
    );
  }

  const level = normalizeImpact(item.impact);

  return (
    <div
      className="ds-ticker-focus"
      data-level={level}
      aria-live="polite"
    >
      <div className="ds-ticker-focus__meta">
        <span className="ds-ticker-focus__index">
          {String(index + 1).padStart(2, "0")}
        </span>
        <span className="ds-ticker-focus__staged">Staged</span>
        <TickerImpact impact={item.impact} />
      </div>

      <p className="ds-ticker-focus__headline">{item.headline}</p>

      <div className="ds-ticker-focus__foot">
        <span className="ds-ticker-focus__source">{item.source}</span>
        {item.published_at ? (
          <span className="ds-ticker-focus__time">
            {item.published_at.slice(0, 16)}
          </span>
        ) : null}
        <span className="ds-ticker-focus__level">{impactLabel(level)}</span>
      </div>

      {item.symbol ? (
        <Link href={`/assets/${item.symbol}`} className="ds-ticker-focus__cta">
          Open {item.symbol} profile →
        </Link>
      ) : (
        <Link href="/news" className="ds-ticker-focus__cta">
          Open news desk →
        </Link>
      )}
    </div>
  );
}
