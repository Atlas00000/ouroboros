"use client";

import type { CSSProperties } from "react";

import { NumberTick } from "@/design/motion/NumberTick";
import {
  driverPolarity,
  formatScore,
  polarityTone,
  type DriverRow,
} from "@/design/patterns/driver-press/driver-utils";

type DriverPressStreamProps = {
  drivers: DriverRow[];
  activeId: string | null;
  onSelect: (id: string) => void;
};

export function DriverPressStream({
  drivers,
  activeId,
  onSelect,
}: DriverPressStreamProps) {
  return (
    <div className="ds-driver-stream" role="list" aria-label="Driver headlines">
      {drivers.map((d, i) => {
        const pol = driverPolarity(d);
        const tone = polarityTone(pol);
        const mag =
          d.contribution == null
            ? 8
            : Math.min(100, Math.abs(d.contribution) * 100);
        const active = d.id === activeId;
        return (
          <button
            key={d.id}
            type="button"
            role="listitem"
            className="ds-driver-row"
            style={
              {
                ["--ds-driver-tone" as string]: tone,
                animationDelay: `${i * 45}ms`,
              } as CSSProperties
            }
            data-active={active ? "true" : "false"}
            data-polarity={pol}
            aria-pressed={active}
            onClick={() => onSelect(d.id)}
          >
            <span className="ds-driver-row__index" aria-hidden>
              {String(i + 1).padStart(2, "0")}
            </span>
            <span className="ds-driver-row__spine" aria-hidden />
            <span className="ds-driver-row__title">{d.title}</span>
            <span className="ds-driver-row__meta">
              {d.source ?? "desk source"}
            </span>
            <span className="ds-driver-row__bar" aria-hidden>
              <span
                className="ds-driver-row__fill"
                style={{ width: `${mag}%` }}
              />
            </span>
            <span className="ds-driver-row__val">
              <NumberTick
                value={
                  d.contribution == null ? "—" : formatScore(d.contribution)
                }
              />
            </span>
          </button>
        );
      })}
    </div>
  );
}
