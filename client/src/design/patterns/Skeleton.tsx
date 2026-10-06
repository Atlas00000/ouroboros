import type { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

type SkeletonProps = HTMLAttributes<HTMLDivElement> & {
  /** Approximate lines for text blocks */
  lines?: number;
};

export function Skeleton({ className, ...props }: SkeletonProps) {
  return (
    <div
      className={cn(
        "ds-skeleton-shimmer rounded-[var(--ds-radius-sm)] bg-[linear-gradient(110deg,var(--ds-plane)_0%,var(--ds-plane-raised)_45%,var(--ds-plane)_90%)] bg-[length:200%_100%] animate-[ds-skeleton_1.4s_var(--ds-ease-in-out-soft)_infinite]",
        className,
      )}
      aria-hidden
      {...props}
    />
  );
}

export function SkeletonText({ lines = 3, className }: { lines?: number; className?: string }) {
  return (
    <div className={cn("space-y-2", className)} role="status" aria-label="Loading">
      {Array.from({ length: lines }, (_, i) => (
        <Skeleton
          key={i}
          className={cn("h-3 w-full", i === lines - 1 && lines > 1 && "w-2/3")}
        />
      ))}
    </div>
  );
}

export function SkeletonMetric({ className }: { className?: string }) {
  return (
    <div className={cn("space-y-2", className)} role="status" aria-label="Loading metric">
      <Skeleton className="h-2.5 w-16" />
      <Skeleton className="h-6 w-24" />
    </div>
  );
}
