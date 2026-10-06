import { cva, type VariantProps } from "class-variance-authority";
import type { InputHTMLAttributes } from "react";

import { cn } from "@/lib/utils";

const inputVariants = cva(
  "w-full rounded-[var(--ds-radius-md)] border border-ds-line bg-ds-canvas-elevated px-3 py-2 font-[family-name:var(--ds-font-ui)] text-[length:var(--ds-text-body)] text-ds-ink placeholder:text-ds-ink-faint transition-[border-color,box-shadow] duration-[var(--ds-duration-swift)] focus-visible:border-ds-signal/60 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-0 focus-visible:outline-ds-signal/40 disabled:opacity-40",
  {
    variants: {
      tone: {
        default: "",
        mono: "font-[family-name:var(--ds-font-numeric)] tabular-nums",
      },
    },
    defaultVariants: {
      tone: "default",
    },
  },
);

export type InputProps = InputHTMLAttributes<HTMLInputElement> &
  VariantProps<typeof inputVariants>;

export function Input({ className, tone, ...props }: InputProps) {
  return <input className={cn(inputVariants({ tone }), className)} {...props} />;
}
