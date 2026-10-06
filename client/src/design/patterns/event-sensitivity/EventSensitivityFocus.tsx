"use client";

import type { CSSProperties } from "react";

import {
  eventFocusBlurb,
  heatLabel,
  heatTone,
  type EventSenseRow,
} from "@/design/patterns/event-sensitivity/event-utils";

type EventSensitivityFocusProps = {
  row: EventSenseRow | null;
};

export function EventSensitivityFocus({ row }: EventSensitivityFocusProps) {
  if (!row) return null;

  return (
    <div
      key={row.event_type}
      className="ds-event-focus"
      style={{ ["--ds-event-tone" as string]: heatTone(row.heat) } as CSSProperties}
      role="status"
    >
      <p className="ds-event-focus__copy">
        <strong>
          {row.event_type} · {heatLabel(row.heat)}
        </strong>
        <span>{eventFocusBlurb(row)}</span>
      </p>
    </div>
  );
}
