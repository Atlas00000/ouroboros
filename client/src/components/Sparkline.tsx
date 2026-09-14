/** Placeholder sparkline — real series wires in W9·D4 / W10. */
export function Sparkline({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 64 24"
      className={className}
      aria-hidden
      preserveAspectRatio="none"
    >
      <polyline
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
        points="0,16 8,14 16,18 24,10 32,12 40,8 48,11 56,6 64,9"
        className="text-muted opacity-70"
      />
    </svg>
  );
}
