"use client";

import type { CSSProperties } from "react";

import { NumberTick } from "@/design/motion/NumberTick";
import {
  driverHeatLabel,
  driverLeadBlurb,
  driverPolarity,
  formatPublished,
  formatScore,
  polarityTone,
  type DriverRow,
} from "@/design/patterns/driver-press/driver-utils";

type DriverPressLeadProps = {
  driver: DriverRow | null;
  index: number;
};

export function DriverPressLead({ driver, index }: DriverPressLeadProps) {
  if (!driver) return null;

  const pol = driverPolarity(driver);
  const tone = polarityTone(pol);
  const published = formatPublished(driver.published_at);

  return (
    <div
      key={driver.id}
      className="ds-driver-lead"
      style={{ ["--ds-driver-tone" as string]: tone } as CSSProperties}
      data-polarity={pol}
    >
      <div className="ds-driver-lead__index" aria-hidden>
        {String(index + 1).padStart(2, "0")}
      </div>
      <div className="ds-driver-lead__body">
        <p className="ds-driver-lead__kicker">
          <span>{driverHeatLabel(driver)}</span>
          <span>{driver.source ?? "desk source"}</span>
          {published ? <span>{published}</span> : null}
        </p>
        <h3 className="ds-driver-lead__title">{driver.title}</h3>
        <p className="ds-driver-lead__blurb">{driverLeadBlurb(driver)}</p>
        <div className="ds-driver-lead__foot">
          <p className="ds-driver-lead__contrib">
            <NumberTick
              value={
                driver.contribution == null
                  ? "—"
                  : formatScore(driver.contribution)
              }
            />
            <span>contrib</span>
          </p>
          {driver.url ? (
            <a
              className="ds-driver-lead__link"
              href={driver.url}
              target="_blank"
              rel="noreferrer"
            >
              Open release
            </a>
          ) : (
            <span className="ds-driver-lead__nolink">No source URL</span>
          )}
        </div>
      </div>
    </div>
  );
}
