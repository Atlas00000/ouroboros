import { cva, type VariantProps } from "class-variance-authority";
import type { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

const surfaceVariants = cva("text-ds-ink", {
  variants: {
    tone: {
      canvas: "bg-ds-canvas",
      elevated: "bg-ds-canvas-elevated",
      plane: "bg-ds-plane shadow-[var(--ds-shadow-plane)]",
      raised: "bg-ds-plane-raised shadow-[var(--ds-shadow-raised)]",
      ghost: "bg-transparent",
    },
    border: {
      none: "border-0",
      hairline: "border border-ds-line",
      strong: "border border-ds-line-strong",
      signal: "border border-ds-signal/40",
    },
    pad: {
      none: "p-0",
      sm: "p-3",
      md: "p-4",
      lg: "p-6",
    },
    radius: {
      none: "rounded-none",
      sm: "rounded-[var(--ds-radius-sm)]",
      md: "rounded-[var(--ds-radius-md)]",
      lg: "rounded-[var(--ds-radius-lg)]",
    },
  },
  defaultVariants: {
    tone: "plane",
    border: "hairline",
    pad: "md",
    radius: "md",
  },
});

export type SurfaceProps = HTMLAttributes<HTMLDivElement> &
  VariantProps<typeof surfaceVariants>;

export function Surface({
  className,
  tone,
  border,
  pad,
  radius,
  ...props
}: SurfaceProps) {
  return (
    <div
      className={cn(surfaceVariants({ tone, border, pad, radius }), className)}
      {...props}
    />
  );
}
