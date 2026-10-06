"use client";

import type { HTMLAttributes, ReactNode } from "react";

import { cn } from "@/lib/utils";

type PageEnterProps = HTMLAttributes<HTMLDivElement> & {
  children: ReactNode;
  /** Second-stage content (rail / body) enters slightly later. */
  delay?: boolean;
};

export function PageEnter({ children, className, delay = false, ...props }: PageEnterProps) {
  return (
    <div
      className={cn(delay ? "ds-page-enter-delay" : "ds-page-enter", className)}
      {...props}
    >
      {children}
    </div>
  );
}
