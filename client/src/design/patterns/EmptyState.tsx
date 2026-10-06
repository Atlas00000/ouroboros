import type { ReactNode } from "react";

import { Surface } from "@/design/primitives/Surface";
import { Text } from "@/design/primitives/Text";
import { cn } from "@/lib/utils";

type EmptyStateProps = {
  title: string;
  children: ReactNode;
  className?: string;
};

/** Copy-only empty — no illustration, emoji, or clip art. */
export function EmptyState({ title, children, className }: EmptyStateProps) {
  return (
    <Surface
      tone="elevated"
      border="hairline"
      pad="md"
      radius="md"
      className={cn("border-dashed", className)}
      role="status"
    >
      <Text as="h2" variant="title" className="text-[length:var(--ds-text-body)]">
        {title}
      </Text>
      <Text as="div" variant="muted" className="mt-2">
        {children}
      </Text>
    </Surface>
  );
}
