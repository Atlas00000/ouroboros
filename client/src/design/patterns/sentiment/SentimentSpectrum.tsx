"use client";

import type { CSSProperties, KeyboardEvent, MouseEvent } from "react";

import {
  polarityTone,
  scoreToPct,
  type SentimentPolarity,
} from "@/design/patterns/sentiment/sentiment-utils";

type SentimentSpectrumProps = {
  score: number;
  polarity: SentimentPolarity;
  onSeek?: (score: number) => void;
};

/**
 * Bipolar −1…+1 track with live needle.
 * Clicking a zone snaps focus probe (does not mutate backend score).
 */
export function SentimentSpectrum({
  score,
  polarity,
  onSeek,
}: SentimentSpectrumProps) {
  const pct = scoreToPct(score);
  const tone = polarityTone(polarity);

  const handleClick = (e: MouseEvent<HTMLDivElement>) => {
    if (!onSeek) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const x = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    onSeek(x * 2 - 1);
  };

  const handleKey = (ev: KeyboardEvent<HTMLDivElement>) => {
    if (!onSeek) return;
    if (ev.key === "ArrowLeft") onSeek(Math.max(-1, score - 0.05));
    if (ev.key === "ArrowRight") onSeek(Math.min(1, score + 0.05));
  };

  return (
    <div className="ds-sent-spectrum" aria-label="Sentiment spectrum">
      <div className="ds-sent-spectrum__axis" aria-hidden>
        <span>−1</span>
        <span>0</span>
        <span>+1</span>
      </div>
      <div
        className="ds-sent-spectrum__track"
        style={{ ["--ds-sent-tone" as string]: tone } as CSSProperties}
        role={onSeek ? "slider" : undefined}
        aria-valuemin={-1}
        aria-valuemax={1}
        aria-valuenow={Number(score.toFixed(2))}
        tabIndex={onSeek ? 0 : undefined}
        onClick={handleClick}
        onKeyDown={handleKey}
      >
        <div className="ds-sent-spectrum__glow ds-sent-spectrum__glow--neg" aria-hidden />
        <div className="ds-sent-spectrum__glow ds-sent-spectrum__glow--pos" aria-hidden />
        <div className="ds-sent-spectrum__zero" aria-hidden />
        <div
          className="ds-sent-spectrum__needle"
          style={{ left: `${pct}%` }}
          data-polarity={polarity}
        >
          <span className="ds-sent-spectrum__pin" />
        </div>
      </div>
      <p className="ds-sent-spectrum__hint">
        Live score pinned on the bipolar track. Arrow keys nudge the focus probe.
      </p>
    </div>
  );
}
