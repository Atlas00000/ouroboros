import type { ReactNode } from "react";

import { NumberTick } from "@/design/motion/NumberTick";
import { Text } from "@/design/primitives/Text";
import { cn } from "@/lib/utils";

export type MetricItem = {
  label: string;
  value: number | string | null | undefined;
  hint?: string;
};

type MetricStripProps = {
  items: MetricItem[];
  className?: string;
  trailing?: ReactNode;
};

/** Horizontal metric rail — hairline dividers, not equal boxed cards. */
export function MetricStrip({ items, className, trailing }: MetricStripProps) {
  return (
    <div
      className={cn(
        "flex flex-wrap items-end gap-x-6 gap-y-3 border-y border-ds-line bg-ds-canvas-elevated/60 px-1 py-3",
        className,
      )}
    >
      {items.map((item, i) => (
        <div
          key={item.label}
          className={cn(
            "min-w-[5.5rem]",
            i > 0 && "border-l border-ds-line pl-6",
          )}
        >
          <Text as="div" variant="micro">
            {item.label}
          </Text>
          <Text as="div" variant="metric" className="mt-1 text-[length:var(--ds-text-title)]">
            <NumberTick value={item.value} />
          </Text>
          {item.hint ? (
            <Text as="div" variant="micro" className="mt-0.5 normal-case tracking-normal">
              {item.hint}
            </Text>
          ) : null}
        </div>
      ))}
      {trailing ? <div className="ml-auto flex items-center gap-2">{trailing}</div> : null}
    </div>
  );
}
