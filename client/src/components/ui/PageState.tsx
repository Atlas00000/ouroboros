import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

export function LoadingState({ children = "Loading…" }: { children?: ReactNode }) {
  return (
    <p className="text-sm text-muted" role="status" aria-live="polite">
      {children}
    </p>
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
    <div
      className={cn("rounded-md border border-border bg-card p-4", className)}
      role="status"
    >
      {title ? <h2 className="text-sm font-medium text-foreground">{title}</h2> : null}
      <div className={cn("text-sm text-muted", title && "mt-2")}>{children}</div>
    </div>
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
    <div
      className={cn("rounded-md border border-regime-trending-down/40 bg-card p-4", className)}
      role="alert"
    >
      <h2 className="text-sm font-medium text-foreground">{title}</h2>
      <div className="mt-2 text-sm text-muted">{children}</div>
    </div>
  );
}
