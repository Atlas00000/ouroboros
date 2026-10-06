"use client";

import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

type StateCrossfadeProps = {
  stateKey: string;
  children: ReactNode;
  className?: string;
};

/** Remount + fade when backend enum / label identity changes. */
export function StateCrossfade({ stateKey, children, className }: StateCrossfadeProps) {
  return (
    <span key={stateKey} className={cn("inline-flex ds-state-fade", className)}>
      {children}
    </span>
  );
}
