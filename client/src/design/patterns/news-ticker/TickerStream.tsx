"use client";

import Link from "next/link";

import {
  impactToneVar,
  normalizeImpact,
} from "@/design/patterns/news-ticker/TickerImpact";
import type { NewsListItem } from "@/lib/api/types";
import { cn } from "@/lib/utils";

type TickerStreamProps = {
  items: NewsListItem[];
  activeId: number | null;
  onActivate: (id: number) => void;
};

/**
 * Depth stream — soft stacked headlines, not brick rows.
 * Lead sits above; stream shows trailing context with opacity falloff.
 */
export function TickerStream({ items, activeId, onActivate }: TickerStreamProps) {
  if (!items.length) {
    return (
      <p className="ds-ticker__empty-filter" role="status">
        No headlines in this cut.
      </p>
    );
  }

  return (
    <ul className="ds-ticker-stream">
      {items.map((item, index) => {
        const level = normalizeImpact(item.impact);
        const active = item.id === activeId;
        const depth = Math.min(index, 4);
        const body = (
          <>
            <span className="ds-ticker-stream__mark" aria-hidden />
            <span className="ds-ticker-stream__text">{item.headline}</span>
            <span className="ds-ticker-stream__meta">
              {item.symbol ? (
                <span className="ds-ticker-stream__sym">{item.symbol}</span>
              ) : (
                <span>{item.source}</span>
              )}
            </span>
          </>
        );

        return (
          <li
            key={item.id}
            className={cn("ds-ticker-stream__item", active && "is-active")}
            data-depth={depth}
            data-level={level}
            style={{ ["--ds-ticker-impact" as string]: impactToneVar(level) }}
            onMouseEnter={() => onActivate(item.id)}
            onFocus={() => onActivate(item.id)}
          >
            {item.symbol ? (
              <Link
                href={`/assets/${item.symbol}`}
                className="ds-ticker-stream__link"
                onFocus={() => onActivate(item.id)}
              >
                {body}
              </Link>
            ) : (
              <button
                type="button"
                className="ds-ticker-stream__link"
                onClick={() => onActivate(item.id)}
                onFocus={() => onActivate(item.id)}
              >
                {body}
              </button>
            )}
          </li>
        );
      })}
    </ul>
  );
}
