import { StaleBadge } from "@/components/StaleBadge";
import { NumberTick } from "@/design/motion/NumberTick";
import {
  dominantDriverPolarity,
  polarityLabel,
  type DriverRow,
} from "@/design/patterns/driver-press/driver-utils";

type DriverPressMastProps = {
  drivers: DriverRow[];
  windowHours?: number;
  stale?: boolean;
};

export function DriverPressMast({
  drivers,
  windowHours,
  stale,
}: DriverPressMastProps) {
  const polarity = dominantDriverPolarity(drivers);

  return (
    <header className="ds-driver-press__mast">
      <p className="ds-driver-press__kicker">
        <span>Driver press</span>
        <StaleBadge stale={stale} />
        {windowHours != null ? <span>{windowHours}h window</span> : null}
      </p>
      <p className="ds-driver-press__count">
        <NumberTick value={drivers.length} />
        <span className="ds-driver-press__count-unit">leads</span>
      </p>
      <p className="ds-driver-press__badge">{polarityLabel(polarity)}</p>
      <p className="ds-driver-press__meta">
        Headlines ranked by contribution to the live sentiment aggregate.
      </p>
    </header>
  );
}
