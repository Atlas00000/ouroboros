"use client";

import type { CSSProperties } from "react";

import { NumberTick } from "@/design/motion/NumberTick";
import {
  atrToPct,
  formatAtr,
  heatTone,
  type EventSenseRow,
} from "@/design/patterns/event-sensitivity/event-utils";

const R = 34;
const C = 2 * Math.PI * R;

type EventSensitivityDialProps = {
  active: EventSenseRow | null;
};

export function EventSensitivityDial({ active }: EventSensitivityDialProps) {
  const pct = atrToPct(active?.atr ?? null);
  const offset = C * (1 - pct / 100);
  const tone = heatTone(active?.heat ?? "pending");

  return (
    <div
      className="ds-event-dial"
      style={{ ["--ds-event-tone" as string]: tone } as CSSProperties}
      data-measured={active?.measured ? "true" : "false"}
    >
      <div className="ds-event-dial__ring">
        <svg className="ds-event-dial__svg" viewBox="0 0 84 84" aria-hidden>
          <circle className="ds-event-dial__track" cx="42" cy="42" r={R} />
          <circle
            key={active?.event_type ?? "empty"}
            className="ds-event-dial__arc"
            cx="42"
            cy="42"
            r={R}
            style={
              {
                strokeDasharray: C,
                strokeDashoffset: offset,
                ["--ds-event-dial-circ" as string]: String(C),
                ["--ds-event-dial-offset" as string]: String(offset),
              } as CSSProperties
            }
          />
        </svg>
        <div className="ds-event-dial__core">
          <p className="ds-event-dial__value">
            <NumberTick value={active?.measured ? formatAtr(active.atr) : "n/a"} />
          </p>
          <p className="ds-event-dial__cap">vs ATR</p>
        </div>
      </div>
      <div className="ds-event-dial__scale" aria-hidden>
        <span>0×</span>
        <span>1.5×</span>
        <span>3×</span>
      </div>
    </div>
  );
}
