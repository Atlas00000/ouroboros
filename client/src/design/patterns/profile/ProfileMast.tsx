import { StaleBadge } from "@/components/StaleBadge";
import { NumberTick } from "@/design/motion/NumberTick";
import { profileHeatLabel, type ProfileHeat } from "@/design/patterns/profile/profile-utils";
import type { AssetProfile } from "@/lib/queries/asset-detail";

type ProfileMastProps = {
  profile: AssetProfile;
  heat: ProfileHeat;
};

export function ProfileMast({ profile, heat }: ProfileMastProps) {
  const id = profile.identity;
  const pair =
    id.base_currency && id.quote_currency
      ? `${id.base_currency}/${id.quote_currency}`
      : null;

  return (
    <header className="ds-profile-dossier__mast">
      <p className="ds-profile-dossier__kicker">
        <span>Living profile</span>
        <StaleBadge stale={profile.provenance.stale} />
        <span>v{profile.profile_version}</span>
      </p>
      {pair ? <p className="ds-profile-dossier__pair">{pair}</p> : null}
      <p className="ds-profile-dossier__heat">{profileHeatLabel(heat)}</p>
      <h2 className="ds-profile-dossier__title">{id.display_name}</h2>
      <p className="ds-profile-dossier__meta">
        <span>
          Class <strong>{id.asset_class}</strong>
        </span>
        {id.mt5_ticker ? (
          <span>
            MT5{" "}
            <strong className="font-[family-name:var(--ds-font-numeric)]">{id.mt5_ticker}</strong>
          </span>
        ) : null}
        {id.venues.length ? (
          <span>
            Venues <strong>{id.venues.join(" · ")}</strong>
          </span>
        ) : null}
        {profile.volatility?.typical_daily_range != null ? (
          <span>
            Typ. range{" "}
            <strong className="font-[family-name:var(--ds-font-numeric)]">
              <NumberTick value={profile.volatility.typical_daily_range.toPrecision(4)} />
            </strong>
          </span>
        ) : null}
      </p>
    </header>
  );
}
