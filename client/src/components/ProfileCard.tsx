import { StaleBadge } from "@/components/StaleBadge";
import type { AssetProfile } from "@/lib/queries/asset-detail";

export function ProfileCard({ profile }: { profile: AssetProfile | null }) {
  if (!profile) {
    return (
      <section className="rounded-md border border-border bg-card p-3">
        <h2 className="text-sm font-medium">Profile</h2>
        <p className="mt-2 text-sm text-muted">No stored profile yet.</p>
      </section>
    );
  }

  const id = profile.identity;
  return (
    <section className="rounded-md border border-border bg-card p-3">
      <div className="flex items-center gap-2">
        <h2 className="text-sm font-medium">Profile</h2>
        <StaleBadge stale={profile.provenance.stale} />
        <span className="text-[10px] text-muted">v{profile.profile_version}</span>
      </div>
      <p className="mt-2 text-sm text-foreground">{id.display_name}</p>
      <dl className="mt-3 grid grid-cols-2 gap-2 text-xs sm:grid-cols-3">
        <div>
          <dt className="text-muted">Class</dt>
          <dd className="capitalize">{id.asset_class}</dd>
        </div>
        <div>
          <dt className="text-muted">Pair</dt>
          <dd className="font-mono">
            {id.base_currency && id.quote_currency
              ? `${id.base_currency}/${id.quote_currency}`
              : "—"}
          </dd>
        </div>
        <div>
          <dt className="text-muted">Venues</dt>
          <dd>{id.venues.join(", ") || "—"}</dd>
        </div>
        <div>
          <dt className="text-muted">ATR pct 30d</dt>
          <dd className="tabular-nums">
            {profile.volatility?.atr_percentile_30d != null
              ? Math.round(profile.volatility.atr_percentile_30d)
              : "—"}
          </dd>
        </div>
        <div>
          <dt className="text-muted">RV pct 30d</dt>
          <dd className="tabular-nums">
            {profile.volatility?.realized_vol_percentile_30d != null
              ? Math.round(profile.volatility.realized_vol_percentile_30d)
              : "—"}
          </dd>
        </div>
      </dl>
      <p className="mt-3 text-[10px] text-muted">
        {profile.provenance.model_version} · as of {profile.as_of}
      </p>
    </section>
  );
}
