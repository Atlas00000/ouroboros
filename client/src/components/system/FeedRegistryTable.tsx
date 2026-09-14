import { EmptyState } from "@/components/ui/PageState";
import type { RegistryResponse } from "@/lib/api/types";
import { cn } from "@/lib/utils";

function statusColor(status: string): string {
  if (status === "ok") return "text-regime-trending-up";
  if (status === "stale") return "text-regime-high-vol";
  if (status === "error") return "text-regime-trending-down";
  return "text-muted";
}

export function FeedRegistryTable({ data }: { data: RegistryResponse | null }) {
  if (!data) {
    return (
      <EmptyState title="Feed registry">
        Unavailable — set <code className="font-mono text-foreground">OUROBOROS_SERVER_API_KEY</code>{" "}
        (admin+) or sign in with an ops/admin Clerk role.
      </EmptyState>
    );
  }

  if (!data.sources.length) {
    return <EmptyState title="Feed registry">No sources registered.</EmptyState>;
  }

  return (
    <section className="rounded-md border border-border bg-card p-3">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <h2 className="text-sm font-medium">Feed registry</h2>
        <span className="text-[10px] text-muted">as of {data.checked_at}</span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[36rem] text-left text-xs">
          <thead className="text-muted">
            <tr className="border-b border-border">
              <th scope="col" className="py-1.5 pr-2 font-medium">
                Source
              </th>
              <th scope="col" className="py-1.5 pr-2 font-medium">
                Kind
              </th>
              <th scope="col" className="py-1.5 pr-2 font-medium">
                Cadence
              </th>
              <th scope="col" className="py-1.5 pr-2 font-medium">
                Age
              </th>
              <th scope="col" className="py-1.5 font-medium">
                Status
              </th>
            </tr>
          </thead>
          <tbody>
            {data.sources.map((s) => (
              <tr key={s.source_id} className="border-b border-border/60">
                <td className="py-1.5 pr-2 font-mono">{s.source_id}</td>
                <td className="py-1.5 pr-2 capitalize text-muted">{s.kind}</td>
                <td className="py-1.5 pr-2 tabular-nums">{s.expected_cadence_seconds}s</td>
                <td className="py-1.5 pr-2 tabular-nums text-muted">
                  {s.age_seconds != null ? `${Math.round(s.age_seconds)}s` : "—"}
                </td>
                <td className={cn("py-1.5 font-medium capitalize", statusColor(s.status))}>
                  {s.status}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
