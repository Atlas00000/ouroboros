"use client";

import { useEffect, useMemo, useState } from "react";

import { DriverPressAtmosphere } from "@/design/patterns/driver-press/DriverPressAtmosphere";
import { DriverPressLead } from "@/design/patterns/driver-press/DriverPressLead";
import { DriverPressMast } from "@/design/patterns/driver-press/DriverPressMast";
import { DriverPressStream } from "@/design/patterns/driver-press/DriverPressStream";
import {
  buildDriverRows,
  dominantDriverPolarity,
} from "@/design/patterns/driver-press/driver-utils";
import { formatAsOfShort } from "@/design/patterns/profile/profile-utils";
import type { SentimentSnapshot } from "@/lib/queries/asset-detail";

import "./driver-press.css";

type DriverPressProps = {
  sentiment: SentimentSnapshot | null;
};

/**
 * Living driver press — ranked headlines from sentiment.v1 top_drivers.
 * Fits Asset page lg:grid-cols-2 beside SentimentField.
 */
export function DriverPress({ sentiment }: DriverPressProps) {
  const drivers = useMemo(
    () => buildDriverRows(sentiment?.top_drivers),
    [sentiment],
  );
  const polarity = useMemo(() => dominantDriverPolarity(drivers), [drivers]);
  const [activeId, setActiveId] = useState<string | null>(null);

  useEffect(() => {
    if (!drivers.length) {
      setActiveId(null);
      return;
    }
    if (!activeId || !drivers.some((d) => d.id === activeId)) {
      setActiveId(drivers[0].id);
    }
  }, [drivers, activeId]);

  const activeIndex = Math.max(
    0,
    drivers.findIndex((d) => d.id === activeId),
  );
  const lead = drivers[activeIndex] ?? drivers[0] ?? null;

  if (!sentiment || drivers.length === 0) {
    return (
      <section
        className="ds-driver-press"
        data-polarity="neutral"
        aria-label="Driver headlines"
      >
        <div className="ds-driver-press__rule" aria-hidden />
        <DriverPressAtmosphere />
        <div className="ds-driver-press__empty">
          <h2>Driver press</h2>
          <p>No driver headlines in this window. They land with scored sentiment.</p>
        </div>
      </section>
    );
  }

  return (
    <section
      className="ds-driver-press"
      data-polarity={polarity}
      aria-label="Driver press"
    >
      <div className="ds-driver-press__rule" aria-hidden />
      <DriverPressAtmosphere />
      <div className="ds-driver-press__body">
        <DriverPressMast
          drivers={drivers}
          windowHours={sentiment.window_hours}
          stale={sentiment.provenance.stale}
        />
        <DriverPressLead driver={lead} index={activeIndex} />
        <DriverPressStream
          drivers={drivers}
          activeId={activeId}
          onSelect={setActiveId}
        />
        <p className="ds-driver-press__foot">
          <span>{sentiment.provenance.model_version}</span>
          <span>as of {formatAsOfShort(sentiment.as_of)}</span>
          <span>top drivers · research only</span>
        </p>
      </div>
    </section>
  );
}
