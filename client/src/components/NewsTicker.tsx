import Link from "next/link";

import type { NewsListItem } from "@/lib/api/types";

export function NewsTicker({ items }: { items: NewsListItem[] }) {
  if (!items.length) {
    return (
      <div className="rounded-md border border-border bg-card px-3 py-2 text-xs text-muted">
        No recent headlines.{" "}
        <Link href="/news" className="text-foreground underline-offset-2 hover:underline">
          Open News
        </Link>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-md border border-border bg-card">
      <div className="flex items-center justify-between border-b border-border px-3 py-1.5">
        <span className="text-[10px] uppercase tracking-wide text-muted">News</span>
        <Link href="/news" className="text-[10px] text-muted hover:text-foreground">
          View all
        </Link>
      </div>
      <ul className="divide-y divide-border">
        {items.slice(0, 6).map((n) => (
          <li key={n.id} className="px-3 py-2">
            {n.symbol ? (
              <Link
                href={`/assets/${n.symbol}`}
                className="text-xs leading-snug text-foreground hover:underline"
              >
                {n.headline}
              </Link>
            ) : (
              <p className="text-xs leading-snug text-foreground">{n.headline}</p>
            )}
            <p className="mt-0.5 text-[10px] text-muted">
              {n.source}
              {n.symbol ? ` · ${n.symbol}` : ""}
              {n.impact ? ` · ${n.impact}` : ""}
            </p>
          </li>
        ))}
      </ul>
    </div>
  );
}
