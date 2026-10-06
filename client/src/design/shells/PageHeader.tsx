import type { ReactNode } from "react";

import { Text } from "@/design/primitives/Text";
import { cn } from "@/lib/utils";

type PageHeaderProps = {
  title: ReactNode;
  description?: ReactNode;
  meta?: ReactNode;
  actions?: ReactNode;
  className?: string;
};

/** Asymmetric page masthead — title plane left, actions right. Not a boxed card. */
export function PageHeader({ title, description, meta, actions, className }: PageHeaderProps) {
  return (
    <header
      className={cn(
        "flex flex-col gap-4 border-b border-ds-line pb-5 sm:flex-row sm:items-end sm:justify-between",
        className,
      )}
    >
      <div className="min-w-0 max-w-2xl space-y-2">
        {meta ? (
          <div className="flex flex-wrap items-center gap-2 text-ds-ink-faint">{meta}</div>
        ) : null}
        <Text as="h1" variant="display">
          {title}
        </Text>
        {description ? (
          <Text as="p" variant="muted" className="max-w-xl">
            {description}
          </Text>
        ) : null}
      </div>
      {actions ? (
        <div className="flex shrink-0 flex-wrap items-center gap-2 sm:justify-end">{actions}</div>
      ) : null}
    </header>
  );
}
