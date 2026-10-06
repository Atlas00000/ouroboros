import { Badge } from "@/design/primitives/Badge";
import { toneForFitTag } from "@/design/map/backend-visual";
import type { FitTag } from "@/lib/api/types";
import { cn } from "@/lib/utils";

type FitTagChipProps = {
  tag?: FitTag | string | null;
  allowOn?: boolean;
  className?: string;
};

export function FitTagChip({ tag, allowOn, className }: FitTagChipProps) {
  if (!tag) {
    return (
      <Badge tone="faint" className={className}>
        Fit —
      </Badge>
    );
  }
  return (
    <Badge
      tone={toneForFitTag(tag)}
      className={cn(allowOn ? "ring-1 ring-ds-ok/40" : undefined, className)}
      title={allowOn ? "Research gate allow_on" : "Research gate off"}
    >
      {String(tag)}
      {allowOn != null ? (allowOn ? " · on" : " · off") : null}
    </Badge>
  );
}
