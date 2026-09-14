import type { WatchdogResponse } from "@/lib/api/types";

export function WatchdogAlertsList({ data }: { data: WatchdogResponse | null }) {
  if (!data) {
    return (
      <section className="rounded-md border border-border bg-card p-3">
        <h2 className="text-sm font-medium">Watchdog</h2>
        <p className="mt-2 text-sm text-muted">No watchdog report available.</p>
      </section>
    );
  }

  return (
    <section className="rounded-md border border-border bg-card p-3">
      <div className="mb-3 flex flex-wrap items-center gap-2">
        <h2 className="text-sm font-medium">Watchdog</h2>
        <span
          className={
            data.ok ? "text-[10px] text-regime-trending-up" : "text-[10px] text-regime-high-vol"
          }
        >
          {data.ok ? "clear" : `${data.alerts.length} alert(s)`}
        </span>
        <span className="text-[10px] text-muted">checked {data.checked_at}</span>
      </div>
      {!data.alerts.length ? (
        <p className="text-sm text-muted">No active feed alerts (weekend price silence suppressed).</p>
      ) : (
        <ul className="space-y-2">
          {data.alerts.map((a) => (
            <li
              key={`${a.source_id}-${a.message}`}
              className="rounded border border-border/80 bg-background/40 px-2 py-2 text-xs"
            >
              <div className="font-mono text-foreground">{a.source_id}</div>
              <p className="mt-1 text-muted">{a.message}</p>
            </li>
          ))}
        </ul>
      )}
      <p className="mt-3 text-[10px] text-muted">
        Stale sources: {data.stale_count}
        {Object.keys(data.rows_marked_stale || {}).length
          ? ` · propagated ${JSON.stringify(data.rows_marked_stale)}`
          : ""}
      </p>
    </section>
  );
}
