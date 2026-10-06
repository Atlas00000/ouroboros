"use client";

import { ChartFrame } from "@/design/patterns/charts";
import { OutboxMix } from "@/design/patterns/desk/OutboxMix";
import { PipeLagChart } from "@/design/patterns/desk/PipeLagChart";
import type { OpsSummaryResponse } from "@/lib/api/types";

export function PipeHealthStrip({ data }: { data: OpsSummaryResponse | null }) {
  if (!data) {
    return (
      <ChartFrame title="Pipe health" empty emptyMessage="Summary unavailable." />
    );
  }

  return (
    <div className="flex flex-col gap-4">
      <ChartFrame
        title="Pipe health"
        meta={
          <span className="text-[10px] text-ds-ink-muted">{data.health_hint}</span>
        }
      >
        <dl className="grid grid-cols-2 gap-3 text-xs sm:grid-cols-4">
          <div>
            <dt className="text-ds-ink-faint">Outbox unpublished</dt>
            <dd className="mt-0.5 font-[family-name:var(--ds-font-numeric)] tabular-nums text-ds-ink">
              {data.outbox_unpublished}
            </dd>
          </div>
          <div>
            <dt className="text-ds-ink-faint">Outbox published</dt>
            <dd className="mt-0.5 font-[family-name:var(--ds-font-numeric)] tabular-nums text-ds-ink">
              {data.outbox_published}
            </dd>
          </div>
          <div>
            <dt className="text-ds-ink-faint">LLM spend (UTC day)</dt>
            <dd className="mt-0.5 font-[family-name:var(--ds-font-numeric)] tabular-nums text-ds-ink">
              ${data.llm_spend_usd_day.toFixed(4)}
            </dd>
          </div>
          <div>
            <dt className="text-ds-ink-faint">As of</dt>
            <dd className="mt-0.5 text-[11px] text-ds-ink-muted">{data.as_of}</dd>
          </div>
        </dl>
      </ChartFrame>
      <div className="grid gap-4 lg:grid-cols-2">
        <OutboxMix
          unpublished={data.outbox_unpublished}
          published={data.outbox_published}
        />
        <PipeLagChart lag={data.ingestion_lag} />
      </div>
    </div>
  );
}
