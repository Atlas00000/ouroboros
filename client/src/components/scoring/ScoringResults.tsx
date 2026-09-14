import { EmptyState } from "@/components/ui/PageState";
import type { WeeklyScoringResponse } from "@/lib/api/types";

export function ScoringResults({ data }: { data: WeeklyScoringResponse | null }) {
  if (!data) {
    return (
      <EmptyState title="Weekly accuracy">
        No reports loaded. Run the weekly scoring job or set{" "}
        <code className="font-mono text-foreground">OUROBOROS_SERVER_API_KEY</code>.
      </EmptyState>
    );
  }

  if (!data.items.length) {
    return (
      <EmptyState title="Weekly accuracy">
        No weekly reports yet — same pipeline as the Resend digest.
      </EmptyState>
    );
  }

  return (
    <div className="space-y-4">
      {data.items.map((week) => (
        <section key={week.id} className="rounded-md border border-border bg-card p-3">
          <div className="flex flex-wrap items-baseline justify-between gap-2">
            <h2 className="text-sm font-medium">
              Week {week.week_start.slice(0, 10)} → {week.week_end.slice(0, 10)}
            </h2>
            <p className="text-xs text-muted">
              {week.n_correct}/{week.n_scored} correct
              {week.accuracy != null ? ` · ${(week.accuracy * 100).toFixed(1)}%` : ""}
            </p>
          </div>
          {week.scoring_model ? (
            <p className="mt-1 text-[10px] text-muted">{week.scoring_model}</p>
          ) : null}
          {week.by_symbol_tf.length ? (
            <div className="mt-3 overflow-x-auto">
              <table className="w-full min-w-[28rem] text-left text-xs">
                <thead className="text-muted">
                  <tr className="border-b border-border">
                    <th scope="col" className="py-1 pr-2 font-medium">
                      Symbol
                    </th>
                    <th scope="col" className="py-1 pr-2 font-medium">
                      TF
                    </th>
                    <th scope="col" className="py-1 pr-2 font-medium">
                      n
                    </th>
                    <th scope="col" className="py-1 pr-2 font-medium">
                      Hit
                    </th>
                    <th scope="col" className="py-1 font-medium">
                      Acc
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {week.by_symbol_tf.map((row) => (
                    <tr
                      key={`${row.symbol}-${row.timeframe}-${row.model_version}`}
                      className="border-b border-border/60"
                    >
                      <td className="py-1 pr-2 font-mono">{row.symbol}</td>
                      <td className="py-1 pr-2">{row.timeframe}</td>
                      <td className="py-1 pr-2 tabular-nums">{row.n}</td>
                      <td className="py-1 pr-2 tabular-nums">{row.correct}</td>
                      <td className="py-1 tabular-nums">
                        {row.accuracy != null ? `${(row.accuracy * 100).toFixed(0)}%` : "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="mt-2 text-sm text-muted">No per-symbol breakdown in this report.</p>
          )}
          <p className="mt-3 text-[10px] text-muted">
            Research context only — not foresight.{" "}
            {week.email_sent_at ? `Email sent ${week.email_sent_at}.` : "Email not sent."}
          </p>
        </section>
      ))}
    </div>
  );
}
