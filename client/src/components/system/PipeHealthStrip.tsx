import type { OpsSummaryResponse } from "@/lib/api/types";

export function PipeHealthStrip({ data }: { data: OpsSummaryResponse | null }) {
  if (!data) {
    return (
      <section className="rounded-md border border-border bg-card p-3">
        <h2 className="text-sm font-medium">Pipe health</h2>
        <p className="mt-2 text-sm text-muted">Summary unavailable.</p>
      </section>
    );
  }

  return (
    <section className="rounded-md border border-border bg-card p-3">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <h2 className="text-sm font-medium">Pipe health</h2>
        <span className="text-[10px] text-muted">{data.health_hint}</span>
      </div>
      <dl className="grid grid-cols-2 gap-3 text-xs sm:grid-cols-4">
        <div>
          <dt className="text-muted">Outbox unpublished</dt>
          <dd className="mt-0.5 tabular-nums text-foreground">{data.outbox_unpublished}</dd>
        </div>
        <div>
          <dt className="text-muted">Outbox published</dt>
          <dd className="mt-0.5 tabular-nums text-foreground">{data.outbox_published}</dd>
        </div>
        <div>
          <dt className="text-muted">LLM spend (UTC day)</dt>
          <dd className="mt-0.5 tabular-nums text-foreground">
            ${data.llm_spend_usd_day.toFixed(4)}
          </dd>
        </div>
        <div>
          <dt className="text-muted">As of</dt>
          <dd className="mt-0.5 text-[11px] text-muted">{data.as_of}</dd>
        </div>
      </dl>
      {data.ingestion_lag.length ? (
        <ul className="mt-4 grid gap-1 text-[11px] text-muted sm:grid-cols-2">
          {data.ingestion_lag.map((row) => (
            <li key={row.source_id} className="flex justify-between gap-2 font-mono">
              <span>{row.source_id}</span>
              <span className="tabular-nums">
                {row.age_seconds != null ? `${Math.round(row.age_seconds)}s` : "never"}
              </span>
            </li>
          ))}
        </ul>
      ) : null}
    </section>
  );
}
