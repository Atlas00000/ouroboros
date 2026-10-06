"use client";

import { NumberTick } from "@/design/motion/NumberTick";
import { cn } from "@/lib/utils";

type PulseMetricProps = {
  label: string;
  value: number | string | null | undefined;
  hint?: string;
  size?: "primary" | "secondary";
  active?: boolean;
  onSelect?: () => void;
};

/** Interactive ledger metric — oversized type, no KPI card chrome. */
export function PulseMetric({
  label,
  value,
  hint,
  size = "secondary",
  active = false,
  onSelect,
}: PulseMetricProps) {
  return (
    <button
      type="button"
      className={cn("ds-pulse-metric")}
      data-size={size}
      data-active={active ? "true" : "false"}
      onClick={onSelect}
      aria-pressed={active}
    >
      <span className="ds-pulse-metric__label">{label}</span>
      <span
        className={cn(
          "ds-pulse-metric__value",
          size === "secondary" && "ds-pulse-metric__value--secondary",
        )}
      >
        <NumberTick value={value} />
      </span>
      {hint ? <span className="ds-pulse-metric__hint">{hint}</span> : null}
      <span className="ds-pulse-metric__underline" aria-hidden />
    </button>
  );
}
