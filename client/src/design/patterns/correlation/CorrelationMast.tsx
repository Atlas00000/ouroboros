import { StaleBadge } from "@/components/StaleBadge";
import type { CorrPeer } from "@/design/patterns/correlation/correlation-utils";

type CorrelationMastProps = {
  peerCount: number;
  windowDays: number | null;
  stale?: boolean;
  bias: "sync" | "split" | "diverge";
  lead: CorrPeer | null;
};

function biasLabel(bias: "sync" | "split" | "diverge"): string {
  if (bias === "sync") return "Sync heavy";
  if (bias === "diverge") return "Diverge heavy";
  return "Split book";
}

export function CorrelationMast({
  peerCount,
  windowDays,
  stale,
  bias,
  lead,
}: CorrelationMastProps) {
  return (
    <header className="ds-corr-field__mast">
      <p className="ds-corr-field__kicker">
        <span>Peer field</span>
        <StaleBadge stale={stale} />
        {windowDays != null ? <span>{windowDays}d window</span> : null}
      </p>
      <p className="ds-corr-field__count">
        <span className="ds-corr-field__count-num">{peerCount}</span>
        <span className="ds-corr-field__count-unit">peers</span>
      </p>
      <p className="ds-corr-field__bias">{biasLabel(bias)}</p>
      <p className="ds-corr-field__meta">
        {lead ? (
          <span>
            Strongest <strong className="font-[family-name:var(--ds-font-numeric)]">{lead.symbol}</strong>
          </span>
        ) : (
          <span>Ranked by absolute coefficient from profile.v1</span>
        )}
      </p>
    </header>
  );
}
