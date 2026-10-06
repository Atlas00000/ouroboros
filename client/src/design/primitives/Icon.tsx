import type { LucideIcon } from "lucide-react";
import type { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

type IconSize = "sm" | "md" | "lg";

const SIZE: Record<IconSize, number> = {
  sm: 14,
  md: 16,
  lg: 20,
};

export type IconProps = HTMLAttributes<HTMLSpanElement> & {
  icon: LucideIcon;
  size?: IconSize;
  label?: string;
};

/** Thin wrapper so icons inherit ink colour and a11y labeling stays consistent. */
export function Icon({
  icon: Lucide,
  size = "md",
  label,
  className,
  ...props
}: IconProps) {
  const px = SIZE[size];
  return (
    <span
      className={cn("inline-flex shrink-0 text-current", className)}
      role={label ? "img" : undefined}
      aria-label={label}
      aria-hidden={label ? undefined : true}
      {...props}
    >
      <Lucide size={px} strokeWidth={1.75} />
    </span>
  );
}
