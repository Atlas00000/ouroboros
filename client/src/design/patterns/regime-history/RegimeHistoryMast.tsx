import { StaleBadge } from "@/components/StaleBadge";
import { NumberTick } from "@/design/motion/NumberTick";
import {
  concentrationLabel,
  formatSharePct,
  type RegimeShareRow,
} from "@/design/patterns/regime-history/regime-history-utils";

type RegimeHistoryMastProps = {
  lead: RegimeShareRow | null;
  sliceCount: number;
  concentration: "dominant" | "lean" | "mixed";
  stale?: boolean;
};

export function RegimeHistoryMast({
  lead,
  sliceCount,
  concentration,
  stale,
}: RegimeHistoryMastProps) {
  return (
    <header className="ds-reg-hist__mast">
      <p className="ds-reg-hist__kicker">
        <span>Regime history</span>
        <StaleBadge stale={stale} />
        <span>{sliceCount} slices</span>
      </p>
      <p className="ds-reg-hist__lead-pct">
        <NumberTick value={lead ? formatSharePct(lead.pct) : null} />
      </p>
      <p className="ds-reg-hist__badge">{concentrationLabel(concentration)}</p>
      <p className="ds-reg-hist__meta">
        {lead ? (
          <span>
            Lead <strong>{lead.label}</strong>
            <span className="ds-reg-hist__meta-key"> · {lead.regime.replaceAll("_", " ")}</span>
          </span>
        ) : (
          <span>Confirmed regime share from profile.v1</span>
        )}
      </p>
    </header>
  );
}
