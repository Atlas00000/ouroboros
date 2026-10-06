"use client";

import { useEffect, useMemo, useState } from "react";

import { CorrelationAtmosphere } from "@/design/patterns/correlation/CorrelationAtmosphere";
import { CorrelationFocus } from "@/design/patterns/correlation/CorrelationFocus";
import { CorrelationMast } from "@/design/patterns/correlation/CorrelationMast";
import { CorrelationPeerRail } from "@/design/patterns/correlation/CorrelationPeerRail";
import { CorrelationSpectrum } from "@/design/patterns/correlation/CorrelationSpectrum";
import {
  corrFieldBias,
  dominantWindow,
  rankCorrPeers,
} from "@/design/patterns/correlation/correlation-utils";
import { formatAsOfShort } from "@/design/patterns/profile/profile-utils";
import type { AssetProfile } from "@/lib/queries/asset-detail";

import "./correlation-field.css";

type CorrelationFieldProps = {
  profile: AssetProfile | null;
};

/**
 * Living peer field — bipolar spectrum + ranked rail from profile.v1 correlations.
 * Fits the Asset page lg:grid-cols-2 cell beside ProfileDossier.
 */
export function CorrelationField({ profile }: CorrelationFieldProps) {
  const peers = useMemo(
    () => rankCorrPeers(profile?.correlations ?? []),
    [profile],
  );
  const bias = useMemo(() => corrFieldBias(peers), [peers]);
  const windowDays = useMemo(() => dominantWindow(peers), [peers]);
  const [active, setActive] = useState<string | null>(null);

  useEffect(() => {
    if (!peers.length) {
      setActive(null);
      return;
    }
    if (!active || !peers.some((p) => p.symbol === active)) {
      setActive(peers[0].symbol);
    }
  }, [peers, active]);

  const focus = peers.find((p) => p.symbol === active) ?? peers[0] ?? null;

  if (!profile || peers.length === 0) {
    return (
      <section className="ds-corr-field" data-bias="split" aria-label="Peer correlations">
        <div className="ds-corr-field__rule" aria-hidden />
        <CorrelationAtmosphere />
        <div className="ds-corr-field__empty">
          <h2>Peer field</h2>
          <p>No peer correlations in this profile cut yet.</p>
        </div>
      </section>
    );
  }

  return (
    <section
      className="ds-corr-field"
      data-bias={bias}
      aria-label="Peer correlation field"
    >
      <div className="ds-corr-field__rule" aria-hidden />
      <CorrelationAtmosphere />
      <div className="ds-corr-field__body">
        <CorrelationMast
          peerCount={peers.length}
          windowDays={windowDays}
          stale={profile.provenance.stale}
          bias={bias}
          lead={peers[0] ?? null}
        />
        <CorrelationSpectrum
          peers={peers}
          activeSymbol={active}
          onSelect={setActive}
        />
        <CorrelationPeerRail
          peers={peers}
          activeSymbol={active}
          onSelect={setActive}
        />
        <CorrelationFocus peer={focus} />
        <p className="ds-corr-field__foot">
          <span>{profile.provenance.model_version}</span>
          <span>as of {formatAsOfShort(profile.as_of)}</span>
          <span>abs ranked · bipolar −1…+1</span>
        </p>
      </div>
    </section>
  );
}
