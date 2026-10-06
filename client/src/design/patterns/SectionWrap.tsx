import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

import "./section-wrap.css";

type SectionWrapProps = {
  children: ReactNode;
  className?: string;
  /** Optional muted label above the wrap. */
  eyebrow?: string;
};

/**
 * Wrapped section prose — ledger voice under titles.
 * One job: orient the reader to what the section does.
 */
export function SectionWrap({ children, className, eyebrow }: SectionWrapProps) {
  return (
    <div className={cn("ds-section-wrap", className)}>
      {eyebrow ? <p className="ds-section-wrap__eyebrow">{eyebrow}</p> : null}
      <p className="ds-section-wrap__body">{children}</p>
    </div>
  );
}
