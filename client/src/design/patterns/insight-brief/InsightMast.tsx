import { StaleBadge } from "@/components/StaleBadge";
import { insightTypeLabel } from "@/design/patterns/insight-brief/insight-utils";
import type { Insight } from "@/lib/queries/asset-detail";

type InsightMastProps = {
  insight: Insight;
};

export function InsightMast({ insight }: InsightMastProps) {
  return (
    <header className="ds-insight-brief__mast">
      <p className="ds-insight-brief__kicker">
        <span>Desk insight</span>
        <StaleBadge stale={insight.provenance.stale} />
        <span>{insightTypeLabel(insight.type)}</span>
        {insight.symbol ? (
          <span className="font-[family-name:var(--ds-font-numeric)]">{insight.symbol}</span>
        ) : null}
      </p>
      <h2 className="ds-insight-brief__title">{insight.title}</h2>
    </header>
  );
}
