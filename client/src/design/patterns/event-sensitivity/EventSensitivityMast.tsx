import { StaleBadge } from "@/components/StaleBadge";
import { NumberTick } from "@/design/motion/NumberTick";
import {
  formatAtr,
  heatLabel,
  type EventSenseRow,
} from "@/design/patterns/event-sensitivity/event-utils";

type EventSensitivityMastProps = {
  lead: EventSenseRow | null;
  total: number;
  measured: number;
  stale?: boolean;
};

export function EventSensitivityMast({
  lead,
  total,
  measured,
  stale,
}: EventSensitivityMastProps) {
  return (
    <header className="ds-event-field__mast">
      <p className="ds-event-field__kicker">
        <span>Event sensitivity</span>
        <StaleBadge stale={stale} />
        <span>
          {measured}/{total} measured
        </span>
      </p>
      <p className="ds-event-field__lead">
        <NumberTick value={lead?.measured ? formatAtr(lead.atr) : "—"} />
        <span className="ds-event-field__lead-unit">ATR</span>
      </p>
      <p className="ds-event-field__badge">
        {lead ? heatLabel(lead.heat) : "No map"}
      </p>
      <p className="ds-event-field__meta">
        {lead ? (
          <span>
            Lead <strong>{lead.event_type}</strong>
            <span className="ds-event-field__meta-sub"> · {lead.label}</span>
          </span>
        ) : (
          <span>Calendar taxonomy from profile.v1</span>
        )}
      </p>
    </header>
  );
}
