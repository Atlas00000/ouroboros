"use client";

import { useEffect, useMemo, useState } from "react";

import { InsightAtmosphere } from "@/design/patterns/insight-brief/InsightAtmosphere";
import { InsightBody } from "@/design/patterns/insight-brief/InsightBody";
import { InsightFocus } from "@/design/patterns/insight-brief/InsightFocus";
import { InsightMast } from "@/design/patterns/insight-brief/InsightMast";
import { InsightRefs } from "@/design/patterns/insight-brief/InsightRefs";
import { InsightTagRail } from "@/design/patterns/insight-brief/InsightTagRail";
import {
  normalizeRefs,
  normalizeTags,
  splitInsightBody,
} from "@/design/patterns/insight-brief/insight-utils";
import { formatAsOfShort } from "@/design/patterns/profile/profile-utils";
import type { Insight } from "@/lib/queries/asset-detail";

import "./insight-brief.css";

type InsightBriefProps = {
  insight: Insight | null;
};

/**
 * Living desk insight — narrative.v1 body with interactive tags and paragraph focus.
 * Full width under AssetSection; capped content width, not oversized.
 */
export function InsightBrief({ insight }: InsightBriefProps) {
  const paragraphs = useMemo(
    () => (insight ? splitInsightBody(insight.body) : []),
    [insight],
  );
  const tags = useMemo(() => normalizeTags(insight?.tags), [insight]);
  const refs = useMemo(() => normalizeRefs(insight?.related_refs), [insight]);

  const [activeTag, setActiveTag] = useState<string | null>(null);
  const [activePara, setActivePara] = useState<string | null>(null);

  useEffect(() => {
    setActiveTag(null);
    setActivePara(paragraphs[0]?.id ?? null);
  }, [insight?.as_of, insight?.title]); // eslint-disable-line react-hooks/exhaustive-deps -- reset on new insight cut

  if (!insight) {
    return (
      <section className="ds-insight-brief" aria-label="Desk insight">
        <div className="ds-insight-brief__rule" aria-hidden />
        <InsightAtmosphere />
        <div className="ds-insight-brief__empty">
          <h2>Desk insight</h2>
          <p>No narrative insight for this cut yet.</p>
        </div>
      </section>
    );
  }

  return (
    <section className="ds-insight-brief" aria-label="Desk insight brief">
      <div className="ds-insight-brief__rule" aria-hidden />
      <InsightAtmosphere />
      <div className="ds-insight-brief__body">
        <InsightMast insight={insight} />
        <InsightBody
          paragraphs={paragraphs}
          activeTag={activeTag}
          activePara={activePara}
          onSelectPara={setActivePara}
        />
        <InsightTagRail tags={tags} activeTag={activeTag} onSelect={setActiveTag} />
        <InsightRefs refs={refs} />
        <InsightFocus insight={insight} activeTag={activeTag} />
        <p className="ds-insight-brief__foot">
          <span>{insight.provenance.model_version}</span>
          <span>as of {formatAsOfShort(insight.as_of)}</span>
          <span>generative narrative · not numeric</span>
        </p>
      </div>
    </section>
  );
}
