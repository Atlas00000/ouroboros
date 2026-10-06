"use client";

import { useMemo, useState } from "react";

import { EmptyState } from "@/components/ui/PageState";
import { ScoringAccuracyTrend } from "@/design/patterns/scoring/ScoringAccuracyTrend";
import { ScoringSymbolBars } from "@/design/patterns/scoring/ScoringSymbolBars";
import type { WeeklyScoringResponse } from "@/lib/api/types";

export function ScoringResults({ data }: { data: WeeklyScoringResponse | null }) {
  const items = data?.items ?? [];
  const [selectedId, setSelectedId] = useState<number | null>(null);

  const selected = useMemo(() => {
    if (!items.length) return null;
    return items.find((w) => w.id === selectedId) ?? items[0];
  }, [items, selectedId]);

  if (!data) {
    return (
      <EmptyState title="Weekly accuracy">
        No reports loaded. Run the weekly scoring job or set{" "}
        <code className="font-mono text-ds-ink">OUROBOROS_SERVER_API_KEY</code>.
      </EmptyState>
    );
  }

  if (!items.length) {
    return (
      <EmptyState title="Weekly accuracy">
        No weekly reports yet — same pipeline as the Resend digest.
      </EmptyState>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <ScoringAccuracyTrend items={items} />
      <ScoringSymbolBars week={selected} />

      <div className="space-y-4">
        {items.map((week) => {
          const active = selected?.id === week.id;
          return (
            <section
              key={week.id}
              className="border-block border-ds-line-strong bg-ds-plane px-3 py-3"
            >
              <button
                type="button"
                className="flex w-full flex-wrap items-baseline justify-between gap-2 text-left"
                onClick={() => setSelectedId(week.id)}
                aria-pressed={active}
              >
                <h2 className="font-[family-name:var(--ds-font-display)] text-[length:var(--ds-text-body)] text-ds-ink">
                  Week {week.week_start.slice(0, 10)} → {week.week_end.slice(0, 10)}
                </h2>
                <p className="font-[family-name:var(--ds-font-numeric)] text-xs text-ds-ink-muted">
                  {week.n_correct}/{week.n_scored} correct
                  {week.accuracy != null ? ` · ${(week.accuracy * 100).toFixed(1)}%` : ""}
                  {active ? " · charted" : ""}
                </p>
              </button>
              {week.scoring_model ? (
                <p className="mt-1 text-[10px] text-ds-ink-faint">{week.scoring_model}</p>
              ) : null}
              {week.fit ? (
                <div className="mt-3 border-t border-ds-line pt-3">
                  <h3 className="font-[family-name:var(--ds-font-ui)] text-[length:var(--ds-text-micro)] uppercase tracking-wider text-ds-ink-muted">
                    Fit stickiness
                  </h3>
                  <p className="mt-1 font-[family-name:var(--ds-font-numeric)] text-xs text-ds-ink">
                    {week.fit.n_correct}/{week.fit.n_scored}
                    {week.fit.accuracy != null
                      ? ` · ${(week.fit.accuracy * 100).toFixed(1)}%`
                      : ""}
                    {week.fit.persistence_accuracy != null
                      ? ` · persistence ${(week.fit.persistence_accuracy * 100).toFixed(1)}%`
                      : ""}
                    {week.fit.delta_vs_persistence != null
                      ? ` · Δ ${(week.fit.delta_vs_persistence * 100).toFixed(1)}pp`
                      : ""}
                  </p>
                  {week.fit.by_family.length ? (
                    <ul className="mt-2 space-y-1 text-xs text-ds-ink-muted">
                      {week.fit.by_family.map((row) => (
                        <li key={`${row.family}-${row.timeframe}`}>
                          <span className="font-mono text-ds-ink">{row.family}</span> {row.timeframe}
                          {": "}
                          {row.correct}/{row.n}
                          {row.accuracy != null ? ` (${(row.accuracy * 100).toFixed(0)}%)` : ""}
                        </li>
                      ))}
                    </ul>
                  ) : null}
                  <p className="mt-1 text-[10px] text-ds-ink-faint">
                    {week.fit.scoring_model ?? "scoring.fit.v1"} — tag stickiness one bar later, not
                    a calendar-month outlook.
                  </p>
                </div>
              ) : null}
              {week.by_symbol_tf.length ? (
                <div className="mt-3 overflow-x-auto">
                  <table className="w-full min-w-[28rem] text-left text-xs">
                    <thead className="text-ds-ink-muted">
                      <tr className="border-b border-ds-line">
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
                          className="border-b border-ds-line/60"
                        >
                          <td className="py-1 pr-2 font-mono">{row.symbol}</td>
                          <td className="py-1 pr-2">{row.timeframe}</td>
                          <td className="py-1 pr-2 tabular-nums">{row.n}</td>
                          <td className="py-1 pr-2 tabular-nums">{row.correct}</td>
                          <td className="py-1 tabular-nums">
                            {row.accuracy != null
                              ? `${(row.accuracy * 100).toFixed(0)}%`
                              : "—"}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="mt-2 text-sm text-ds-ink-muted">
                  No per-symbol breakdown in this report.
                </p>
              )}
              <p className="mt-3 text-[10px] text-ds-ink-faint">
                Research context only — not foresight.{" "}
                {week.email_sent_at ? `Email sent ${week.email_sent_at}.` : "Email not sent."}
              </p>
            </section>
          );
        })}
      </div>
    </div>
  );
}
