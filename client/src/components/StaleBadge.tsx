import { Badge } from "@/design/primitives/Badge";
import { toneForStale } from "@/design/map/backend-visual";

export function StaleBadge({ stale }: { stale?: boolean }) {
  if (!stale) return null;
  return (
    <Badge tone={toneForStale(true)} role="status" aria-label="Data may be stale">
      Stale
    </Badge>
  );
}
