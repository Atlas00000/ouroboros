"use client";

import { useMemo, useState } from "react";

import { ProfileAtmosphere } from "@/design/patterns/profile/ProfileAtmosphere";
import { ProfileMast } from "@/design/patterns/profile/ProfileMast";
import { ProfileSessionRail } from "@/design/patterns/profile/ProfileSessionRail";
import { ProfileVolField } from "@/design/patterns/profile/ProfileVolField";
import {
  buildProfileMeters,
  formatAsOfShort,
  profileHeat,
  type ProfileMeterId,
} from "@/design/patterns/profile/profile-utils";
import type { AssetProfile } from "@/lib/queries/asset-detail";

import "./profile-dossier.css";

type ProfileDossierProps = {
  profile: AssetProfile | null;
};

/**
 * Living profile plane — identity, interactive vol meters, live session rail.
 * Fits the Asset page lg:grid-cols-2 cell; no Bootstrap card chrome.
 */
export function ProfileDossier({ profile }: ProfileDossierProps) {
  const meters = useMemo(
    () => (profile ? buildProfileMeters(profile) : []),
    [profile],
  );
  const heat = useMemo(() => (profile ? profileHeat(profile) : "calm"), [profile]);
  const [active, setActive] = useState<ProfileMeterId>("atr");

  if (!profile) {
    return (
      <section className="ds-profile-dossier" aria-label="Profile">
        <div className="ds-profile-dossier__rule" aria-hidden />
        <ProfileAtmosphere />
        <div className="ds-profile-dossier__empty">
          <h2>Profile</h2>
          <p>No stored profile yet — wait for daily_profiles or an event refresh.</p>
        </div>
      </section>
    );
  }

  return (
    <section
      className="ds-profile-dossier"
      data-heat={heat}
      aria-label="Living profile"
    >
      <div className="ds-profile-dossier__rule" aria-hidden />
      <ProfileAtmosphere />
      <div className="ds-profile-dossier__body">
        <ProfileMast profile={profile} heat={heat} />
        <ProfileVolField meters={meters} active={active} onSelect={setActive} />
        <ProfileSessionRail profile={profile} />
        <p className="ds-profile-dossier__foot">
          <span>{profile.provenance.model_version}</span>
          <span>as of {formatAsOfShort(profile.as_of)}</span>
          {profile.liquidity?.notes ? <span>{profile.liquidity.notes}</span> : null}
        </p>
      </div>
    </section>
  );
}
