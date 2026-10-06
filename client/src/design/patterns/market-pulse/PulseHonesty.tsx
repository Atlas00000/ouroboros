import { StateCrossfade } from "@/design/motion/StateCrossfade";
import { Badge } from "@/design/primitives/Badge";
import { Text } from "@/design/primitives/Text";
import { toneForStale } from "@/design/map/backend-visual";

type PulseHonestyProps = {
  stale?: boolean;
  generatedAt?: string;
};

/** Freshness + research boundary — horizontal ledger note, not a side card. */
export function PulseHonesty({ stale, generatedAt }: PulseHonestyProps) {
  const freshnessKey = stale ? "stale" : "fresh";
  const freshnessLabel = stale ? "Stale ledger" : "Fresh cut";

  return (
    <aside className="ds-pulse-honesty" aria-label="Data honesty">
      <div className="ds-pulse-honesty__row">
        <span className="ds-pulse-honesty__eyebrow">Honesty</span>
        <StateCrossfade stateKey={freshnessKey}>
          <Badge tone={toneForStale(Boolean(stale))}>{freshnessLabel}</Badge>
        </StateCrossfade>
        {generatedAt ? (
          <Text as="p" variant="mono" className="ds-pulse-honesty__asof">
            as of {generatedAt}
          </Text>
        ) : (
          <Text as="p" variant="muted" className="ds-pulse-honesty__asof">
            Awaiting list provenance
          </Text>
        )}
      </div>
      <Text as="p" variant="micro" className="ds-pulse-honesty__note">
        Research context only. No execution. Sibling platforms consume this desk —
        they do not trade from it.
      </Text>
    </aside>
  );
}
