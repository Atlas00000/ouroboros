import { cva, type VariantProps } from "class-variance-authority";
import type { ButtonHTMLAttributes } from "react";

import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 rounded-[var(--ds-radius-md)] font-[family-name:var(--ds-font-ui)] text-[length:var(--ds-text-label)] font-[number:var(--ds-font-weight-medium)] tracking-wide transition-[background,color,border-color,opacity] duration-[var(--ds-duration-swift)] ease-[var(--ds-ease-out-soft)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ds-signal disabled:pointer-events-none disabled:opacity-40",
  {
    variants: {
      variant: {
        primary: "bg-ds-signal text-[color:var(--ds-signal-ink)] hover:brightness-110",
        secondary:
          "border border-ds-line-strong bg-ds-plane-raised text-ds-ink hover:border-ds-signal/50",
        ghost: "bg-transparent text-ds-ink-muted hover:bg-ds-plane-raised hover:text-ds-ink",
        danger: "border border-ds-halt/40 bg-ds-halt/10 text-ds-halt hover:bg-ds-halt/20",
      },
      size: {
        sm: "h-8 px-3",
        md: "h-9 px-4",
        lg: "h-10 px-5",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "md",
    },
  },
);

export type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> &
  VariantProps<typeof buttonVariants>;

export function Button({ className, variant, size, type = "button", ...props }: ButtonProps) {
  return (
    <button
      type={type}
      className={cn(buttonVariants({ variant, size }), className)}
      {...props}
    />
  );
}
