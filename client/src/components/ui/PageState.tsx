import type { ReactNode } from "react";

import { EmptyState as DesignEmpty } from "@/design/patterns/EmptyState";
import { SkeletonText } from "@/design/patterns/Skeleton";
import { Surface } from "@/design/primitives/Surface";
import { Text } from "@/design/primitives/Text";
import { cn } from "@/lib/utils";

export function LoadingState({ children = "Loading…" }: { children?: ReactNode }) {
  return (
    <div className="space-y-3" role="status" aria-live="polite">
      <SkeletonText lines={3} />
      <Text as="p" variant="muted" className="sr-only">
        {children}
      </Text>
    </div>
  );
}

export function EmptyState({
  title,
  children,
  className,
}: {
  title?: string;
  children: ReactNode;
  className?: string;
}) {
  return (
    <DesignEmpty title={title ?? "Nothing here"} className={className}>
      {children}
    </DesignEmpty>
  );
}

export function ErrorState({
  title = "Something went wrong",
  children,
  className,
}: {
  title?: string;
  children: ReactNode;
  className?: string;
}) {
  return (
    <Surface
      tone="plane"
      border="hairline"
      pad="md"
      className={cn("border-ds-halt/35", className)}
      role="alert"
    >
      <Text as="h2" variant="title" className="text-[length:var(--ds-text-body)] text-ds-halt">
        {title}
      </Text>
      <Text as="div" variant="muted" className="mt-2">
        {children}
      </Text>
    </Surface>
  );
}
