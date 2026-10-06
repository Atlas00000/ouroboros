"use client";

import type { CSSProperties } from "react";

import {
  driverFocusBlurb,
  polarityLabel,
  polarityTone,
  sentimentFocusBlurb,
  sentimentPolarity,
  type SentimentDriverRow,
  type SentimentPolarity,
} from "@/design/patterns/sentiment/sentiment-utils";

type SentimentFocusProps = {
  mode: "score" | "driver";
  score: number;
  polarity: SentimentPolarity;
  itemCount: number;
  windowHours: number;
  driver: SentimentDriverRow | null;
};

export function SentimentFocus({
  mode,
  score,
  polarity,
  itemCount,
  windowHours,
  driver,
}: SentimentFocusProps) {
  const tone =
    mode === "driver" && driver
      ? polarityTone(sentimentPolarity(driver.contribution ?? 0))
      : polarityTone(polarity);

  const title =
    mode === "driver" && driver
      ? `${driver.source ?? "Driver"} · ${polarityLabel(sentimentPolarity(driver.contribution ?? 0))}`
      : `${polarityLabel(polarity)} · live score`;

  const body =
    mode === "driver" && driver
      ? driverFocusBlurb(driver)
      : sentimentFocusBlurb(score, polarity, itemCount, windowHours);

  return (
    <div
      key={mode === "driver" && driver ? driver.id : "score"}
      className="ds-sent-focus"
      style={{ ["--ds-sent-tone" as string]: tone } as CSSProperties}
      role="status"
    >
      <p className="ds-sent-focus__copy">
        <strong>{title}</strong>
        <span>{body}</span>
      </p>
      {mode === "driver" && driver?.url ? (
        <a
          className="ds-sent-focus__link"
          href={driver.url}
          target="_blank"
          rel="noreferrer"
        >
          Open source
        </a>
      ) : null}
    </div>
  );
}
