"use client";

import Link from "next/link";

import {
  impactToneVar,
  normalizeImpact,
} from "@/design/patterns/news-ticker/TickerImpact";
import type { NewsListItem } from "@/lib/api/types";
import { cn } from "@/lib/utils";

type TickerHeadlineProps = {
  item: NewsListItem;
  index: number;
  active?: boolean;
  onActivate?: () => void;
};

/** Tape row — ledger index + impact spine; interactive, not a card. */
export function TickerHeadline({
  item,
  index,
  active,
  onActivate,
}: TickerHeadlineProps) {
  const level = normalizeImpact(item.impact);
  const tone = impactToneVar(level);

  const inner = (
    <>
      <span className="ds-ticker-headline__rail" aria-hidden>
        <span className="ds-ticker-headline__spine" />
      </span>
      <span className="ds-ticker-headline__index">
        {String(index + 1).padStart(2, "0")}
      </span>
      <div className="ds-ticker-headline__body">
        <p className="ds-ticker-headline__text">{item.headline}</p>
        <div className="ds-ticker-headline__meta">
          <span className="ds-ticker-headline__source">{item.source}</span>
          {item.symbol ? (
            <span className="ds-ticker-headline__symbol">{item.symbol}</span>
          ) : null}
        </div>
      </div>
    </>
  );

  const className = cn("ds-ticker-headline", active && "is-active");
  const style = { ["--ds-ticker-impact" as string]: tone };

  if (item.symbol) {
    return (
      <li
        className={className}
        data-level={level}
        style={style}
        onMouseEnter={onActivate}
        onFocus={onActivate}
      >
        <Link
          href={`/assets/${item.symbol}`}
          className="ds-ticker-headline__link"
          onFocus={onActivate}
        >
          {inner}
        </Link>
      </li>
    );
  }

  return (
    <li
      className={className}
      data-level={level}
      style={style}
      onMouseEnter={onActivate}
      onFocus={onActivate}
    >
      <button
        type="button"
        className="ds-ticker-headline__link"
        onClick={onActivate}
        onFocus={onActivate}
      >
        {inner}
      </button>
    </li>
  );
}
