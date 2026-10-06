"use client";

import type { CSSProperties } from "react";

import { NumberTick } from "@/design/motion/NumberTick";
import {
  formatScore,
  polarityTone,
  sentimentPolarity,
  type SentimentDriverRow,
} from "@/design/patterns/sentiment/sentiment-utils";

type SentimentDriverPeekProps = {
  drivers: SentimentDriverRow[];
  activeId: string | null;
  onSelect: (id: string) => void;
};

export function SentimentDriverPeek({
  drivers,
  activeId,
  onSelect,
}: SentimentDriverPeekProps) {
  if (!drivers.length) return null;

  return (
    <div className="ds-sent-peek" role="list" aria-label="Top drivers">
      {drivers.map((d, i) => {
        const c = d.contribution ?? 0;
        const pol = sentimentPolarity(c);
        const tone = polarityTone(pol);
        const mag = Math.min(100, Math.abs(c) * 100);
        const active = d.id === activeId;
        return (
          <button
            key={d.id}
            type="button"
            role="listitem"
            className="ds-sent-peek__row"
            style={
              {
                ["--ds-sent-tone" as string]: tone,
                animationDelay: `${i * 40}ms`,
              } as CSSProperties
            }
            data-active={active ? "true" : "false"}
            aria-pressed={active}
            onClick={() => onSelect(d.id)}
          >
            <span className="ds-sent-peek__title">{d.title}</span>
            <span className="ds-sent-peek__bar" aria-hidden>
              <span className="ds-sent-peek__fill" style={{ width: `${mag}%` }} />
            </span>
            <span className="ds-sent-peek__val">
              <NumberTick value={d.contribution == null ? "—" : formatScore(d.contribution)} />
            </span>
          </button>
        );
      })}
    </div>
  );
}
