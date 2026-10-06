"use client";

import {
  defaultDisclaimer,
  insightFocusBlurb,
} from "@/design/patterns/insight-brief/insight-utils";
import type { Insight } from "@/lib/queries/asset-detail";

type InsightFocusProps = {
  insight: Insight;
  activeTag: string | null;
};

export function InsightFocus({ insight, activeTag }: InsightFocusProps) {
  return (
    <div className="ds-insight-focus" role="status">
      <p className="ds-insight-focus__copy">
        <strong>{activeTag ? "Tag focus" : "Briefing note"}</strong>
        <span>{insightFocusBlurb(insight, activeTag)}</span>
      </p>
      <p className="ds-insight-focus__disclaimer">
        {defaultDisclaimer(insight.disclaimer?.text)}
      </p>
    </div>
  );
}
