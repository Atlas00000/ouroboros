import { cn } from "@/lib/utils";

type UniverseVolBarProps = {
  value?: number | null;
  className?: string;
};

/** Vol character as an intensity fill — not a boxed KPI. */
export function UniverseVolBar({ value, className }: UniverseVolBarProps) {
  if (value == null || Number.isNaN(value)) {
    return (
      <div className={cn("ds-universe-vol", className)} data-empty="true">
        <span className="ds-universe-vol__label">vol</span>
        <span className="ds-universe-vol__value">—</span>
      </div>
    );
  }

  const clamped = Math.max(0, Math.min(100, value));
  const hot = clamped >= 75;

  return (
    <div className={cn("ds-universe-vol", className)} data-hot={hot ? "true" : "false"}>
      <div className="ds-universe-vol__meta">
        <span className="ds-universe-vol__label">vol</span>
        <span className="ds-universe-vol__value">{Math.round(clamped)}%</span>
      </div>
      <div className="ds-universe-vol__track" aria-hidden>
        <div
          className="ds-universe-vol__fill"
          style={{ width: `${clamped}%` }}
        />
      </div>
    </div>
  );
}
