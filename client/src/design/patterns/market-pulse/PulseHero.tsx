"use client";

import { PulseLiveMark } from "@/design/patterns/market-pulse/PulseLiveMark";
import {
  PULSE_FOCUS_COPY,
  type PulseFocus,
} from "@/design/patterns/market-pulse/types";

type PulseHeroProps = {
  focus: PulseFocus;
};

/** Section herald — display title + live mark + focus narration. */
export function PulseHero({ focus }: PulseHeroProps) {
  return (
    <header className="ds-market-pulse__hero">
      <div className="ds-market-pulse__hero-top">
        <div>
          <p className="ds-market-pulse__eyebrow">Research desk</p>
          <h2 className="ds-market-pulse__title">
            Market pulse
            <span className="ds-market-pulse__ghost" aria-hidden>
              LEDGER
            </span>
          </h2>
        </div>
        <PulseLiveMark />
      </div>
      <p className="ds-market-pulse__focus-copy" aria-live="polite">
        {PULSE_FOCUS_COPY[focus]}
      </p>
    </header>
  );
}
