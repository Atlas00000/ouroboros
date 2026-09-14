import type { AssetProfile } from "@/lib/queries/asset-detail";
import { cn } from "@/lib/utils";

export function CorrelationHeatmap({ profile }: { profile: AssetProfile | null }) {
  const rows = profile?.correlations ?? [];
  if (!rows.length) {
    return (
      <section className="rounded-md border border-border bg-card p-3">
        <h2 className="text-sm font-medium">Correlations</h2>
        <p className="mt-2 text-sm text-muted">No peer correlations in profile.</p>
      </section>
    );
  }

  return (
    <section className="rounded-md border border-border bg-card p-3">
      <h2 className="text-sm font-medium">Correlations</h2>
      <ul className="mt-3 space-y-2">
        {rows.map((r) => {
          const pct = Math.round(((r.coefficient + 1) / 2) * 100);
          const hot = Math.abs(r.coefficient) >= 0.6;
          return (
            <li key={`${r.symbol}-${r.window_days}`} className="flex items-center gap-2 text-xs">
              <span className="w-16 font-mono text-foreground">{r.symbol}</span>
              <div className="h-2 flex-1 overflow-hidden rounded bg-border">
                <div
                  className={cn("h-full rounded", hot ? "bg-accent" : "bg-muted")}
                  style={{ width: `${pct}%` }}
                />
              </div>
              <span className="w-12 tabular-nums text-right text-muted">
                {r.coefficient.toFixed(2)}
              </span>
            </li>
          );
        })}
      </ul>
      <p className="mt-2 text-[10px] text-muted">Window days shown per row in profile payload.</p>
    </section>
  );
}
