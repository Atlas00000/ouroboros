"use client";

import { useEffect, useMemo, useState } from "react";

import { formatAsOfShort } from "@/design/patterns/profile/profile-utils";
import { SentimentAtmosphere } from "@/design/patterns/sentiment/SentimentAtmosphere";
import { SentimentDial } from "@/design/patterns/sentiment/SentimentDial";
import { SentimentDriverPeek } from "@/design/patterns/sentiment/SentimentDriverPeek";
import { SentimentFocus } from "@/design/patterns/sentiment/SentimentFocus";
import { SentimentMast } from "@/design/patterns/sentiment/SentimentMast";
import { SentimentSpectrum } from "@/design/patterns/sentiment/SentimentSpectrum";
import {
  buildDriverRows,
  formatScore,
  sentimentPolarity,
} from "@/design/patterns/sentiment/sentiment-utils";
import type { SentimentSnapshot } from "@/lib/queries/asset-detail";

import "./sentiment-field.css";

type SentimentFieldProps = {
  sentiment: SentimentSnapshot | null;
};

/**
 * Living sentiment plane — bipolar score + driver peek from sentiment.v1.
 * Fits Asset page lg:grid-cols-2 beside Drivers.
 */
export function SentimentField({ sentiment }: SentimentFieldProps) {
  const drivers = useMemo(
    () => buildDriverRows(sentiment?.top_drivers),
    [sentiment],
  );
  const liveScore = sentiment?.score ?? 0;
  const livePolarity = sentimentPolarity(liveScore);

  const [probe, setProbe] = useState(liveScore);
  const [activeDriver, setActiveDriver] = useState<string | null>(null);

  useEffect(() => {
    setProbe(liveScore);
    setActiveDriver(null);
  }, [liveScore, sentiment?.as_of]);

  const probePolarity = sentimentPolarity(probe);
  const focusDriver = drivers.find((d) => d.id === activeDriver) ?? null;
  const mode = focusDriver ? "driver" : "score";

  if (!sentiment) {
    return (
      <section className="ds-sent-field" data-polarity="neutral" aria-label="Sentiment">
        <div className="ds-sent-field__rule" aria-hidden />
        <SentimentAtmosphere />
        <div className="ds-sent-field__empty">
          <h2>Sentiment</h2>
          <p>No sentiment in the current window. Score lands after news is scored in the 24h cut.</p>
        </div>
      </section>
    );
  }

  return (
    <section
      className="ds-sent-field"
      data-polarity={livePolarity}
      aria-label="Sentiment field"
    >
      <div className="ds-sent-field__rule" aria-hidden />
      <SentimentAtmosphere />
      <div className="ds-sent-field__body">
        <SentimentMast
          score={liveScore}
          polarity={livePolarity}
          itemCount={sentiment.item_count}
          windowHours={sentiment.window_hours}
          stale={sentiment.provenance.stale}
        />
        <div className="ds-sent-field__split">
          <SentimentDial score={probe} polarity={probePolarity} />
          <SentimentSpectrum
            score={probe}
            polarity={probePolarity}
            onSeek={(s) => {
              setActiveDriver(null);
              setProbe(s);
            }}
          />
        </div>
        <SentimentDriverPeek
          drivers={drivers}
          activeId={activeDriver}
          onSelect={(id) => {
            setActiveDriver(id);
            const d = drivers.find((x) => x.id === id);
            if (d?.contribution != null) setProbe(d.contribution);
          }}
        />
        <SentimentFocus
          mode={mode}
          score={liveScore}
          polarity={livePolarity}
          itemCount={sentiment.item_count}
          windowHours={sentiment.window_hours}
          driver={focusDriver}
        />
        <p className="ds-sent-field__foot">
          <span>{sentiment.provenance.model_version}</span>
          <span>as of {formatAsOfShort(sentiment.as_of)}</span>
          <span>live {formatScore(liveScore)}</span>
        </p>
      </div>
    </section>
  );
}
