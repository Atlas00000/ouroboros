import { StaleBadge } from "@/components/StaleBadge";
import { NumberTick } from "@/design/motion/NumberTick";
import { REGIME_LABEL } from "@/design/map/backend-visual";
import {
  formatProbPct,
  type NowcastProb,
} from "@/design/patterns/regime-nowcast/nowcast-utils";

type RegimeNowcastMastProps = {
  activeRegime: string;
  lead: NowcastProb | null;
  timeframe?: string;
  stale?: boolean;
};

export function RegimeNowcastMast({
  activeRegime,
  lead,
  timeframe,
  stale,
}: RegimeNowcastMastProps) {
  const activeLabel = REGIME_LABEL[activeRegime] ?? activeRegime.replaceAll("_", " ");

  return (
    <header className="ds-reg-now__mast">
      <p className="ds-reg-now__kicker">
        <span>Live nowcast</span>
        <StaleBadge stale={stale} />
        {timeframe ? <span>{timeframe}</span> : null}
      </p>
      <p className="ds-reg-now__lead-pct">
        <NumberTick value={lead ? formatProbPct(lead.pct) : null} />
      </p>
      <p className="ds-reg-now__badge">{activeLabel}</p>
      <p className="ds-reg-now__meta">
        Soft regime probabilities for the current cut. History sits in the peer cell.
      </p>
    </header>
  );
}
