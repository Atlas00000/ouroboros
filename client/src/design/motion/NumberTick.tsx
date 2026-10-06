"use client";

import { useEffect, useRef, useState, type HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

type NumberTickProps = HTMLAttributes<HTMLSpanElement> & {
  value: number | string | null | undefined;
  fallback?: string;
};

/** Brief opacity settle when the displayed metric changes. */
export function NumberTick({
  value,
  fallback = "—",
  className,
  ...props
}: NumberTickProps) {
  const display = value == null || value === "" ? fallback : String(value);
  const prev = useRef(display);
  const [tick, setTick] = useState(0);

  useEffect(() => {
    if (prev.current === display) return;
    prev.current = display;
    setTick((n) => n + 1);
  }, [display]);

  return (
    <span
      key={tick}
      className={cn(
        "inline-block font-[family-name:var(--ds-font-numeric)] tabular-nums",
        tick > 0 && "ds-number-tick",
        className,
      )}
      {...props}
    >
      {display}
    </span>
  );
}
