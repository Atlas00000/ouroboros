"use client";

import type { DeskHeroStageId } from "@/design/patterns/desk-hero/types";

type DeskHeroAtmosphereProps = {
  stage: DeskHeroStageId;
};

/**
 * Stage-tinted ledger atmosphere — token washes only.
 * No illustration, emoji, or decorative clip art.
 */
export function DeskHeroAtmosphere({ stage }: DeskHeroAtmosphereProps) {
  return (
    <div className="ds-desk-hero__atmosphere" data-stage={stage} aria-hidden>
      <div className="ds-desk-hero__wash ds-desk-hero__wash--base" />
      <div className="ds-desk-hero__wash ds-desk-hero__wash--focus" />
      <div className="ds-desk-hero__rule" />
      <div className="ds-desk-hero__grain" />
    </div>
  );
}
