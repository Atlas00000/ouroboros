import { cn } from "@/lib/utils";

export type ImpactLevel = "high" | "medium" | "low" | "unknown";

export function normalizeImpact(raw?: string | null): ImpactLevel {
  const s = (raw ?? "").toLowerCase().trim();
  if (!s) return "unknown";
  if (s === "high" || s === "critical" || s === "severe") return "high";
  if (s === "medium" || s === "med" || s === "moderate") return "medium";
  if (s === "low" || s === "minor") return "low";
  return "unknown";
}

export function impactLabel(level: ImpactLevel): string {
  switch (level) {
    case "high":
      return "High";
    case "medium":
      return "Medium";
    case "low":
      return "Low";
    default:
      return "Unrated";
  }
}

/** CSS custom property for impact tone (tokens only). */
export function impactToneVar(level: ImpactLevel): string {
  switch (level) {
    case "high":
      return "var(--ds-halt)";
    case "medium":
      return "var(--ds-warn)";
    case "low":
      return "var(--ds-signal)";
    default:
      return "var(--ds-ink-faint)";
  }
}

type TickerImpactProps = {
  impact?: string | null;
  className?: string;
  compact?: boolean;
};

/** Impact mark — typography + intensity bar, not a chip pile. */
export function TickerImpact({ impact, className, compact }: TickerImpactProps) {
  const level = normalizeImpact(impact);

  return (
    <span
      className={cn("ds-ticker-impact", compact && "is-compact", className)}
      data-level={level}
      style={{ ["--ds-ticker-impact" as string]: impactToneVar(level) }}
    >
      <span className="ds-ticker-impact__label">{impactLabel(level)}</span>
      {!compact ? (
        <span className="ds-ticker-impact__bar" aria-hidden>
          <span className="ds-ticker-impact__fill" data-level={level} />
        </span>
      ) : null}
    </span>
  );
}
