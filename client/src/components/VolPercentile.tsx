import { cn } from "@/lib/utils";

export function VolPercentile({ value }: { value?: number | null }) {
  if (value == null || Number.isNaN(value)) {
    return <span className="tabular-nums text-muted text-xs">—</span>;
  }
  const hot = value >= 75;
  return (
    <span
      className={cn(
        "tabular-nums text-xs",
        hot ? "text-regime-high-vol" : "text-muted",
      )}
    >
      {Math.round(value)}%
    </span>
  );
}
