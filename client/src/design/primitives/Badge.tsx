import { cva, type VariantProps } from "class-variance-authority";
import type { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-[var(--ds-radius-sm)] px-1.5 py-0.5 font-[family-name:var(--ds-font-ui)] text-[length:var(--ds-text-micro)] font-[number:var(--ds-font-weight-medium)] uppercase tracking-[var(--ds-text-micro-tracking)]",
  {
    variants: {
      tone: {
        signal: "bg-ds-signal-soft text-ds-signal",
        ok: "bg-[color:var(--ds-ok-soft)] text-ds-ok",
        warn: "bg-[color:var(--ds-warn-soft)] text-ds-warn",
        halt: "bg-[color:var(--ds-halt-soft)] text-ds-halt",
        idle: "bg-[color:var(--ds-idle-soft)] text-ds-idle",
        vol: "bg-[color:var(--ds-vol-soft)] text-ds-vol",
        faint: "bg-ds-plane-raised text-ds-ink-faint",
      },
    },
    defaultVariants: {
      tone: "idle",
    },
  },
);

export type BadgeProps = HTMLAttributes<HTMLSpanElement> &
  VariantProps<typeof badgeVariants>;

export function Badge({ className, tone, ...props }: BadgeProps) {
  return <span className={cn(badgeVariants({ tone }), className)} {...props} />;
}

/** Alias for chip-style usage in later section work. */
export const Chip = Badge;
