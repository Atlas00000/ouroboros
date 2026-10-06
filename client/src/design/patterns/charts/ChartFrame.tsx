import type { ReactNode } from "react";

import { StaleBadge } from "@/components/StaleBadge";
import { Text } from "@/design/primitives/Text";
import { cn } from "@/lib/utils";

import "./charts.css";

type ChartFrameProps = {
  title: string;
  meta?: ReactNode;
  stale?: boolean;
  loading?: boolean;
  empty?: boolean;
  emptyMessage?: string;
  className?: string;
  children?: ReactNode;
};

/** Shared chart chrome — hairline plane, honesty slots, no Bootstrap card stack. */
export function ChartFrame({
  title,
  meta,
  stale,
  loading,
  empty,
  emptyMessage = "No series available",
  className,
  children,
}: ChartFrameProps) {
  return (
    <section className={cn("ds-chart-frame", className)} aria-label={title}>
      <header className="ds-chart-frame__head">
        <div className="ds-chart-frame__title-row">
          <Text as="h2" variant="label" className="ds-chart-frame__title">
            {title}
          </Text>
          <StaleBadge stale={stale} />
          {meta}
        </div>
      </header>
      {loading ? (
        <p className="ds-chart-frame__status" role="status">
          Loading series…
        </p>
      ) : empty ? (
        <p className="ds-chart-frame__status" role="status">
          {emptyMessage}
        </p>
      ) : (
        <div className="ds-chart-frame__body">{children}</div>
      )}
    </section>
  );
}
