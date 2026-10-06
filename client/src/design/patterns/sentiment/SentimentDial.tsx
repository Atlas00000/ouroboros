"use client";

import type { CSSProperties } from "react";

import { NumberTick } from "@/design/motion/NumberTick";
import {
  formatScore,
  polarityTone,
  scoreMagnitudePct,
  type SentimentPolarity,
} from "@/design/patterns/sentiment/sentiment-utils";

const R = 34;
const C = 2 * Math.PI * R;

type SentimentDialProps = {
  score: number;
  polarity: SentimentPolarity;
};

export function SentimentDial({ score, polarity }: SentimentDialProps) {
  const mag = scoreMagnitudePct(score);
  const offset = C * (1 - mag / 100);
  const tone = polarityTone(polarity);

  return (
    <div
      className="ds-sent-dial"
      style={{ ["--ds-sent-tone" as string]: tone } as CSSProperties}
      data-polarity={polarity}
    >
      <div className="ds-sent-dial__ring">
        <svg className="ds-sent-dial__svg" viewBox="0 0 84 84" aria-hidden>
          <circle className="ds-sent-dial__track" cx="42" cy="42" r={R} />
          <circle
            key={score.toFixed(3)}
            className="ds-sent-dial__arc"
            cx="42"
            cy="42"
            r={R}
            style={
              {
                strokeDasharray: C,
                strokeDashoffset: offset,
                ["--ds-sent-dial-circ" as string]: String(C),
                ["--ds-sent-dial-offset" as string]: String(offset),
              } as CSSProperties
            }
          />
        </svg>
        <div className="ds-sent-dial__core">
          <p className="ds-sent-dial__value">
            <NumberTick value={formatScore(score)} />
          </p>
          <p className="ds-sent-dial__cap">[-1, +1]</p>
        </div>
      </div>
    </div>
  );
}
