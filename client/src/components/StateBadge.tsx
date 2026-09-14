import { cn } from "@/lib/utils";

const LABELS: Record<string, string> = {
  trending_up: "Up",
  trending_down: "Down",
  ranging: "Range",
  high_volatility: "High vol",
};

const COLORS: Record<string, string> = {
  trending_up: "bg-regime-trending-up/20 text-regime-trending-up",
  trending_down: "bg-regime-trending-down/20 text-regime-trending-down",
  ranging: "bg-regime-ranging/20 text-regime-ranging",
  high_volatility: "bg-regime-high-vol/20 text-regime-high-vol",
};

export function StateBadge({ regime }: { regime?: string | null }) {
  if (!regime) {
    return (
      <span className="rounded px-1.5 py-0.5 text-[10px] uppercase tracking-wide text-muted">
        —
      </span>
    );
  }
  return (
    <span
      className={cn(
        "rounded px-1.5 py-0.5 text-[10px] font-medium uppercase tracking-wide",
        COLORS[regime] ?? "bg-border text-muted",
      )}
    >
      {LABELS[regime] ?? regime}
    </span>
  );
}
