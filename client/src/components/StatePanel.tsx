import { StaleBadge } from "@/components/StaleBadge";
import type { MarketState } from "@/lib/queries/asset-detail";
import { cn } from "@/lib/utils";

export function StatePanel({ state }: { state: MarketState | null }) {
  if (!state) {
    return (
      <section className="rounded-md border border-border bg-card p-3">
        <h2 className="text-sm font-medium">State</h2>
        <p className="mt-2 text-sm text-muted">No market state for this symbol.</p>
      </section>
    );
  }

  return (
    <section className="rounded-md border border-border bg-card p-3">
      <div className="flex items-center gap-2">
        <h2 className="text-sm font-medium">State</h2>
        <StaleBadge stale={state.provenance.stale} />
      </div>
      <dl className="mt-3 grid grid-cols-2 gap-3 text-xs sm:grid-cols-4">
        <div>
          <dt className="text-muted">Regime</dt>
          <dd className="mt-0.5 font-medium capitalize text-foreground">
            {state.regime.replaceAll("_", " ")}
          </dd>
        </div>
        <div>
          <dt className="text-muted">Vol pct</dt>
          <dd className="mt-0.5 tabular-nums">
            {state.volatility_percentile != null
              ? `${Math.round(state.volatility_percentile)}`
              : "—"}
          </dd>
        </div>
        <div>
          <dt className="text-muted">Trend ER</dt>
          <dd className="mt-0.5 tabular-nums">
            {state.trend_strength != null ? state.trend_strength.toFixed(2) : "—"}
          </dd>
        </div>
        <div>
          <dt className="text-muted">Confidence</dt>
          <dd className="mt-0.5 tabular-nums">{state.provenance.confidence.toFixed(2)}</dd>
        </div>
      </dl>
      <ul className="mt-4 space-y-1.5">
        {state.regime_probabilities.map((p) => (
          <li key={p.regime} className="flex items-center gap-2 text-[11px]">
            <span className="w-28 capitalize text-muted">{p.regime.replaceAll("_", " ")}</span>
            <div className="h-1.5 flex-1 overflow-hidden rounded bg-border">
              <div
                className={cn("h-full rounded bg-accent")}
                style={{ width: `${Math.round(p.probability * 100)}%` }}
              />
            </div>
            <span className="tabular-nums text-muted w-10 text-right">
              {(p.probability * 100).toFixed(0)}%
            </span>
          </li>
        ))}
      </ul>
      <p className="mt-3 text-[10px] text-muted">
        {state.provenance.model_version} · as of {state.as_of} · generated{" "}
        {state.provenance.generated_at}
      </p>
    </section>
  );
}
