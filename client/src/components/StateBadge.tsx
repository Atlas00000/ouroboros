import { Badge } from "@/design/primitives/Badge";
import { StateCrossfade } from "@/design/motion/StateCrossfade";
import { REGIME_LABEL, toneForRegime } from "@/design/map/backend-visual";

export function StateBadge({ regime }: { regime?: string | null }) {
  if (!regime) {
    return <Badge tone="faint">—</Badge>;
  }
  const tone = toneForRegime(regime);
  return (
    <StateCrossfade stateKey={regime}>
      <Badge tone={tone}>{REGIME_LABEL[regime] ?? regime}</Badge>
    </StateCrossfade>
  );
}
