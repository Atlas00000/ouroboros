import { StaleBadge } from "@/components/StaleBadge";

export function MarketSummaryStrip({
  assetCount,
  highImpactCount,
  stale,
  generatedAt,
}: {
  assetCount: number;
  highImpactCount?: number;
  stale?: boolean;
  generatedAt?: string;
}) {
  return (
    <div className="flex flex-wrap items-center gap-x-4 gap-y-2 rounded-md border border-border bg-card px-3 py-2">
      <span className="text-xs font-medium text-foreground">Market</span>
      <span className="tabular-nums text-xs text-muted">{assetCount} assets</span>
      {typeof highImpactCount === "number" ? (
        <span className="tabular-nums text-xs text-muted">
          {highImpactCount} high-impact headlines
        </span>
      ) : null}
      <StaleBadge stale={stale} />
      {generatedAt ? (
        <span className="text-[10px] text-muted">list {generatedAt}</span>
      ) : null}
      <span className="text-[10px] text-muted">
        Research only — not investment advice · no execution
      </span>
    </div>
  );
}
