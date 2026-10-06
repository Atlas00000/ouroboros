"use client";

import type { CSSProperties } from "react";
import { useEffect, useMemo, useState } from "react";

import { cssVarForTone, toneForRegime, type Regime } from "@/design/map/backend-visual";
import { RegimeNowcastAtmosphere } from "@/design/patterns/regime-nowcast/RegimeNowcastAtmosphere";
import { RegimeNowcastDial } from "@/design/patterns/regime-nowcast/RegimeNowcastDial";
import { RegimeNowcastFocus } from "@/design/patterns/regime-nowcast/RegimeNowcastFocus";
import { RegimeNowcastMast } from "@/design/patterns/regime-nowcast/RegimeNowcastMast";
import { RegimeNowcastMetrics } from "@/design/patterns/regime-nowcast/RegimeNowcastMetrics";
import { RegimeNowcastStack } from "@/design/patterns/regime-nowcast/RegimeNowcastStack";
import { buildNowcastProbs } from "@/design/patterns/regime-nowcast/nowcast-utils";
import type { MarketState } from "@/lib/queries/asset-detail";

import "./regime-nowcast.css";

type RegimeNowcastFieldProps = {
  state: MarketState | null;
};

/**
 * Living nowcast plane — soft regime probabilities from state.v1.
 * Fits Asset page lg:grid-cols-2 beside RegimeHistoryField.
 */
export function RegimeNowcastField({ state }: RegimeNowcastFieldProps) {
  const rows = useMemo(
    () => buildNowcastProbs(state?.regime_probabilities),
    [state],
  );
  const lead = rows[0] ?? null;
  const [active, setActive] = useState<string | null>(null);

  useEffect(() => {
    if (!state || !rows.length) {
      setActive(null);
      return;
    }
    if (!active || !rows.some((r) => r.regime === active)) {
      const prefer = rows.find((r) => r.regime === state.regime) ?? rows[0];
      setActive(prefer.regime);
    }
  }, [state, rows, active]);

  const focus = rows.find((r) => r.regime === active) ?? lead;
  const toneColor = cssVarForTone(toneForRegime((state?.regime ?? lead?.regime) as Regime));

  if (!state || rows.length === 0) {
    return (
      <section className="ds-reg-now" aria-label="Live nowcast">
        <div className="ds-reg-now__rule" aria-hidden />
        <RegimeNowcastAtmosphere />
        <div className="ds-reg-now__empty">
          <h2>Live nowcast</h2>
          <p>No market state for this symbol yet.</p>
        </div>
      </section>
    );
  }

  return (
    <section
      className="ds-reg-now"
      style={{ ["--ds-reg-tone" as string]: toneColor } as CSSProperties}
      aria-label="Live regime nowcast"
    >
      <div className="ds-reg-now__rule" aria-hidden />
      <RegimeNowcastAtmosphere />
      <div className="ds-reg-now__body">
        <RegimeNowcastMast
          activeRegime={state.regime}
          lead={lead}
          timeframe={state.timeframe}
          stale={state.provenance.stale}
        />
        <RegimeNowcastMetrics
          volPct={state.volatility_percentile}
          trendEr={state.trend_strength}
          confidence={state.provenance.confidence}
          asOf={state.as_of}
        />
        <RegimeNowcastDial
          rows={rows}
          active={focus}
          liveRegime={state.regime}
          onSelect={setActive}
        />
        <RegimeNowcastStack
          rows={rows}
          activeRegime={active}
          onSelect={setActive}
        />
        <RegimeNowcastFocus row={focus} liveRegime={state.regime} />
        <p className="ds-reg-now__foot">
          <span>{state.provenance.model_version}</span>
          <span>generated {state.provenance.generated_at}</span>
          <span>soft probs · not history share</span>
        </p>
      </div>
    </section>
  );
}
