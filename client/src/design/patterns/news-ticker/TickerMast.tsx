"use client";

import Link from "next/link";

import { HOME_COPY } from "@/design/patterns/home-copy";
import { SectionWrap } from "@/design/patterns/SectionWrap";

type TickerMastProps = {
  count: number;
  live?: boolean;
};

/** Slim living mast for Drivers — title + wrap prose. */
export function TickerMast({ count, live = true }: TickerMastProps) {
  return (
    <header className="ds-ticker__mast">
      <div>
        <p className="ds-ticker__eyebrow">
          {live ? <span className="ds-ticker__live" aria-hidden /> : null}
          {HOME_COPY.drivers.eyebrow}
        </p>
        <h2 className="ds-ticker__title">Drivers</h2>
        <SectionWrap className="ds-section-wrap--rail ds-ticker__wrap">
          {HOME_COPY.drivers.wrap}
        </SectionWrap>
        <p className="ds-ticker__subtitle">{count} headlines in cut</p>
      </div>
      <Link href="/news" className="ds-ticker__all">
        Full tape →
      </Link>
    </header>
  );
}
