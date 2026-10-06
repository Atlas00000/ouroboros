import { cva, type VariantProps } from "class-variance-authority";
import type { ElementType, HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

const textVariants = cva("", {
  variants: {
    variant: {
      display:
        "font-[family-name:var(--ds-font-display)] text-[length:var(--ds-text-display)] leading-[var(--ds-text-display-lh)] tracking-[var(--ds-text-display-tracking)] font-semibold text-ds-ink",
      title:
        "font-[family-name:var(--ds-font-display)] text-[length:var(--ds-text-title)] leading-[var(--ds-text-title-lh)] tracking-[var(--ds-text-title-tracking)] font-semibold text-ds-ink",
      body: "font-[family-name:var(--ds-font-ui)] text-[length:var(--ds-text-body)] leading-[var(--ds-text-body-lh)] font-normal text-ds-ink",
      muted:
        "font-[family-name:var(--ds-font-ui)] text-[length:var(--ds-text-body)] leading-[var(--ds-text-body-lh)] text-ds-ink-muted",
      label:
        "font-[family-name:var(--ds-font-ui)] text-[length:var(--ds-text-label)] leading-[var(--ds-text-label-lh)] tracking-[var(--ds-text-label-tracking)] font-medium uppercase text-ds-ink-muted",
      micro:
        "font-[family-name:var(--ds-font-ui)] text-[length:var(--ds-text-micro)] leading-[var(--ds-text-micro-lh)] tracking-[var(--ds-text-micro-tracking)] uppercase text-ds-ink-faint",
      metric:
        "font-[family-name:var(--ds-font-numeric)] text-[length:var(--ds-text-body)] leading-[var(--ds-text-body-lh)] tabular-nums text-ds-ink",
      mono:
        "font-[family-name:var(--ds-font-numeric)] text-[length:var(--ds-text-label)] leading-[var(--ds-text-label-lh)] tabular-nums text-ds-ink",
    },
  },
  defaultVariants: {
    variant: "body",
  },
});

type TextOwnProps = {
  as?: ElementType;
};

export type TextProps = HTMLAttributes<HTMLElement> &
  TextOwnProps &
  VariantProps<typeof textVariants>;

export function Text({
  as: Comp = "p",
  className,
  variant,
  ...props
}: TextProps) {
  return <Comp className={cn(textVariants({ variant }), className)} {...props} />;
}
