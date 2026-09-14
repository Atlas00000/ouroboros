import { cn } from "@/lib/utils";

export function StaleBadge({ stale }: { stale?: boolean }) {
  if (!stale) return null;
  return (
    <span
      role="status"
      aria-label="Data may be stale"
      className={cn(
        "rounded px-1.5 py-0.5 text-[10px] font-medium uppercase tracking-wide",
        "bg-stale/15 text-stale",
      )}
    >
      Stale
    </span>
  );
}
