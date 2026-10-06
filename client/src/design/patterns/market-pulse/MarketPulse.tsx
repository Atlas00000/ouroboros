"use client";

import { useCallback, useMemo, useState, type PointerEvent } from "react";

import { PageEnter } from "@/design/motion/PageEnter";
import { PulseAtmosphere } from "@/design/patterns/market-pulse/PulseAtmosphere";
import { PulseHero } from "@/design/patterns/market-pulse/PulseHero";
import { PulseHonesty } from "@/design/patterns/market-pulse/PulseHonesty";
import { PulseMetric } from "@/design/patterns/market-pulse/PulseMetric";
import { PulseSpectrum } from "@/design/patterns/market-pulse/PulseSpectrum";
import {
  emptyRegimeMix,
  mixFromRegimes,
  type PulseFocus,
  type PulseRegimeMix,
} from "@/design/patterns/market-pulse/types";
import { cssVarForTone, toneForRegime } from "@/design/map/backend-visual";

import "./market-pulse.css";

export type MarketPulseProps = {
  assetCount: number;
  highImpactCount?: number;
  regimes?: Array<string | null | undefined>;
  regimeMix?: PulseRegimeMix;
  stale?: boolean;
  generatedAt?: string;
};

function toneForFocus(focus: PulseFocus): string {
  if (focus === "assets") return "var(--ds-signal)";
  if (focus === "impact") return "var(--ds-halt)";
  return cssVarForTone(toneForRegime(focus));
}

/**
 * Market pulse — cinematic living-ledger herald for Home.
 * Pointer-reactive atmosphere, interactive metrics + regime spectrum.
 */
export function MarketPulse({
  assetCount,
  highImpactCount,
  regimes,
  regimeMix: regimeMixProp,
  stale,
  generatedAt,
}: MarketPulseProps) {
  const [focus, setFocus] = useState<PulseFocus>("assets");
  const impact =
    typeof highImpactCount === "number" ? highImpactCount : null;

  const mix = useMemo(() => {
    if (regimeMixProp) return regimeMixProp;
    if (regimes?.length) return mixFromRegimes(regimes);
    return emptyRegimeMix();
  }, [regimeMixProp, regimes]);

  const onPointerMove = useCallback((e: PointerEvent<HTMLElement>) => {
    const el = e.currentTarget;
    const rect = el.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / Math.max(rect.width, 1)) * 100;
    const y = ((e.clientY - rect.top) / Math.max(rect.height, 1)) * 100;
    el.style.setProperty("--ds-pulse-mx", `${x.toFixed(2)}%`);
    el.style.setProperty("--ds-pulse-my", `${y.toFixed(2)}%`);
  }, []);

  const onPointerLeave = useCallback((e: PointerEvent<HTMLElement>) => {
    e.currentTarget.style.setProperty("--ds-pulse-mx", "62%");
    e.currentTarget.style.setProperty("--ds-pulse-my", "28%");
  }, []);

  return (
    <PageEnter>
      <section
        className="ds-market-pulse"
        aria-label="Market pulse"
        data-focus={focus}
        style={{ ["--ds-pulse-tone" as string]: toneForFocus(focus) }}
        onPointerMove={onPointerMove}
        onPointerLeave={onPointerLeave}
      >
        <PulseAtmosphere focus={focus} />

        <div className="ds-market-pulse__content">
          <PulseHero focus={focus} />

          <div className="ds-market-pulse__stage">
            <PulseMetric
              label="Universe"
              value={assetCount}
              hint="active assets on watch"
              size="primary"
              active={focus === "assets"}
              onSelect={() => setFocus("assets")}
            />
            <PulseMetric
              label="High impact"
              value={impact}
              hint="headlines in current cut"
              size="secondary"
              active={focus === "impact"}
              onSelect={() => setFocus("impact")}
            />
          </div>

          <PulseSpectrum
            mix={mix}
            focus={focus}
            onFocus={setFocus}
            totalAssets={assetCount}
          />

          <PulseHonesty stale={stale} generatedAt={generatedAt} />
        </div>
      </section>
    </PageEnter>
  );
}
