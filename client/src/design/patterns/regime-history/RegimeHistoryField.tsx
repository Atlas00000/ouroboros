"use client";

import type { CSSProperties } from "react";
import { useEffect, useMemo, useState } from "react";

import { formatAsOfShort } from "@/design/patterns/profile/profile-utils";
import { RegimeHistoryAtmosphere } from "@/design/patterns/regime-history/RegimeHistoryAtmosphere";
import { RegimeHistoryDial } from "@/design/patterns/regime-history/RegimeHistoryDial";
import { RegimeHistoryFocus } from "@/design/patterns/regime-history/RegimeHistoryFocus";
import { RegimeHistoryMast } from "@/design/patterns/regime-history/RegimeHistoryMast";
import { RegimeHistoryStack } from "@/design/patterns/regime-history/RegimeHistoryStack";
import {
  buildRegimeShares,
  dominantShare,
  historyConcentration,
} from "@/design/patterns/regime-history/regime-history-utils";
import type { AssetProfile } from "@/lib/queries/asset-detail";

import "./regime-history.css";

type RegimeHistoryFieldProps = {
  profile: AssetProfile | null;
};

/**
 * Living regime history plane — confirmed share from profile.v1.
 * Fits Asset page lg:grid-cols-2 beside live state probabilities.
 */
export function RegimeHistoryField({ profile }: RegimeHistoryFieldProps) {
  const rows = useMemo(
    () => buildRegimeShares(profile?.regime_distribution),
    [profile],
  );
  const lead = useMemo(() => dominantShare(rows), [rows]);
  const concentration = useMemo(() => historyConcentration(lead), [lead]);
  const [active, setActive] = useState<string | null>(null);

  useEffect(() => {
    if (!rows.length) {
      setActive(null);
      return;
    }
    if (!active || !rows.some((r) => r.regime === active)) {
      setActive(rows[0].regime);
    }
  }, [rows, active]);

  const focus = rows.find((r) => r.regime === active) ?? lead;

  if (!profile || rows.length === 0) {
    return (
      <section className="ds-reg-hist" aria-label="Regime history">
        <div className="ds-reg-hist__rule" aria-hidden />
        <RegimeHistoryAtmosphere />
        <div className="ds-reg-hist__empty">
          <h2>Regime history</h2>
          <p>No historical regime share in this profile cut yet.</p>
        </div>
      </section>
    );
  }

  return (
    <section
      className="ds-reg-hist"
      style={
        {
          ["--ds-reg-tone" as string]: lead?.color ?? "var(--ds-signal)",
        } as CSSProperties
      }
      aria-label="Regime history field"
    >
      <div className="ds-reg-hist__rule" aria-hidden />
      <RegimeHistoryAtmosphere />
      <div className="ds-reg-hist__body">
        <RegimeHistoryMast
          lead={lead}
          sliceCount={rows.length}
          concentration={concentration}
          stale={profile.provenance.stale}
        />
        <RegimeHistoryDial rows={rows} active={focus} onSelect={setActive} />
        <RegimeHistoryStack
          rows={rows}
          activeRegime={active}
          onSelect={setActive}
        />
        <RegimeHistoryFocus row={focus} />
        <p className="ds-reg-hist__foot">
          <span>{profile.provenance.model_version}</span>
          <span>as of {formatAsOfShort(profile.as_of)}</span>
          <span>confirmed share · not live probs</span>
        </p>
      </div>
    </section>
  );
}
