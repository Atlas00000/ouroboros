import type { SentimentSnapshot } from "@/lib/queries/asset-detail";

export function DriverHeadlines({ sentiment }: { sentiment: SentimentSnapshot | null }) {
  const drivers = sentiment?.top_drivers ?? [];
  if (!drivers.length) {
    return (
      <section className="rounded-md border border-border bg-card p-3">
        <h2 className="text-sm font-medium">Drivers</h2>
        <p className="mt-2 text-sm text-muted">No driver headlines.</p>
      </section>
    );
  }

  return (
    <section className="rounded-md border border-border bg-card p-3">
      <h2 className="text-sm font-medium">Drivers</h2>
      <ul className="mt-3 divide-y divide-border">
        {drivers.map((d, i) => (
          <li key={`${d.title}-${i}`} className="py-2">
            {d.url ? (
              <a
                href={d.url}
                target="_blank"
                rel="noreferrer"
                className="text-xs text-foreground hover:underline"
              >
                {d.title}
              </a>
            ) : (
              <p className="text-xs text-foreground">{d.title}</p>
            )}
            <p className="mt-0.5 text-[10px] text-muted">
              {d.source ?? "source"}
              {d.contribution != null ? ` · contrib ${d.contribution.toFixed(2)}` : ""}
            </p>
          </li>
        ))}
      </ul>
    </section>
  );
}
