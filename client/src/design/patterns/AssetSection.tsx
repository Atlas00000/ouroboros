import type { ReactNode } from "react";

import { SectionWrap } from "@/design/patterns/SectionWrap";
import { cn } from "@/lib/utils";

type AssetSectionProps = {
  eyebrow: string;
  wrap: string;
  children: ReactNode;
  className?: string;
};

/** Dossier section: eyebrow + wrap prose, then the working surface. */
export function AssetSection({ eyebrow, wrap, children, className }: AssetSectionProps) {
  return (
    <section className={cn("flex flex-col gap-3", className)}>
      <SectionWrap eyebrow={eyebrow}>{wrap}</SectionWrap>
      {children}
    </section>
  );
}
