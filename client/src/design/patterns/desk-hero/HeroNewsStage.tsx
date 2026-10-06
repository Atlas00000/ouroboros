import Link from "next/link";

import type { NewsListItem } from "@/lib/api/types";
import {
  impactLabel,
  impactToneVar,
  normalizeImpact,
} from "@/design/patterns/news-ticker";

type HeroNewsStageProps = {
  items: NewsListItem[];
};

/** News desk — high-impact narrative context, not a feed wall. */
export function HeroNewsStage({ items }: HeroNewsStageProps) {
  const cut = items.slice(0, 5);

  return (
    <div className="ds-hero-stage ds-hero-stage--news">
      <div className="ds-hero-stage__lead">
        <p className="ds-hero-stage__kicker">Narrative pressure</p>
        <p className="ds-hero-stage__lede">
          Headlines feeding sentiment — research context for sibling platforms.
        </p>
      </div>

      {!cut.length ? (
        <p className="ds-hero-stage__empty">No high-impact headlines in the current cut.</p>
      ) : (
        <ul className="ds-hero-news__list">
          {cut.map((item) => {
            const impact = normalizeImpact(item.impact);
            return (
              <li key={item.id} className="ds-hero-news__item">
                <span
                  className="ds-hero-news__impact"
                  style={{ ["--ds-impact-tone" as string]: impactToneVar(impact) }}
                >
                  {impactLabel(impact)}
                </span>
                <div className="ds-hero-news__body">
                  <p className="ds-hero-news__headline">{item.headline}</p>
                  <p className="ds-hero-news__meta">
                    <span>{item.source}</span>
                    {item.symbol ? (
                      <>
                        <span aria-hidden>·</span>
                        <Link
                          href={`/assets/${item.symbol}`}
                          className="ds-hero-news__sym"
                        >
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
                  </p>
                </div>
              </li>
            );
          })}
        </ul>
      )}

      <Link href="/news" className="ds-hero-news__more">
        Open news desk →
      </Link>
    </div>
  );
}
