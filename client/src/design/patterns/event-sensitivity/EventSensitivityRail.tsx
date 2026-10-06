"use client";

import type { CSSProperties } from "react";

import { NumberTick } from "@/design/motion/NumberTick";
import {
  atrToPct,
  formatAtr,
  heatTone,
  type EventSenseRow,
} from "@/design/patterns/event-sensitivity/event-utils";

type EventSensitivityRailProps = {
  rows: EventSenseRow[];
  activeType: string | null;
  onSelect: (eventType: string) => void;
};

export function EventSensitivityRail({
  rows,
  activeType,
  onSelect,
}: EventSensitivityRailProps) {
  return (
    <div className="ds-event-rail" role="list" aria-label="Event types">
      {rows.map((row, i) => {
        const active = row.event_type === activeType;
        const mag = atrToPct(row.atr);
        return (
          <button
            key={row.event_type}
            type="button"
            role="listitem"
            className="ds-event-tile"
            style={
              {
                ["--ds-event-tone" as string]: heatTone(row.heat),
                animationDelay: `${i * 45}ms`,
              } as CSSProperties
            }
            data-active={active ? "true" : "false"}
            data-heat={row.heat}
            data-measured={row.measured ? "true" : "false"}
            aria-pressed={active}
            onClick={() => onSelect(row.event_type)}
          >
            <span className="ds-event-tile__type">{row.event_type}</span>
            <span className="ds-event-tile__label">{row.label}</span>
            <span className="ds-event-tile__bar" aria-hidden>
              <span
                className="ds-event-tile__fill"
                style={{ width: row.measured ? `${mag}%` : "12%" }}
              />
            </span>
            <span className="ds-event-tile__atr">
              <NumberTick value={row.measured ? formatAtr(row.atr) : "pending"} />
            </span>
          </button>
        );
      })}
    </div>
  );
}
