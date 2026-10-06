import type { ReactNode } from "react";

import { Text } from "@/design/primitives/Text";
import { cn } from "@/lib/utils";

type ActionRailProps = {
  /** When omitted or empty, the rail title is hidden (child owns the mast). */
  title?: string;
  children: ReactNode;
  className?: string;
};

/**
 * Narrow context / actions column. Visually secondary to the primary plane —
 * hairline left edge on desktop, not an equal card stack.
 */
export function ActionRail({ title, children, className }: ActionRailProps) {
  return (
    <aside
      className={cn(
        "flex w-full flex-col gap-3 lg:w-[var(--ds-rail-width)] lg:shrink-0 lg:border-l lg:border-ds-line lg:pl-5",
        className,
      )}
      aria-label={title || "Context"}
    >
      {title ? (
        <Text as="h2" variant="label">
          {title}
        </Text>
      ) : null}
      <div className="flex min-h-0 flex-1 flex-col gap-3">{children}</div>
    </aside>
  );
}
