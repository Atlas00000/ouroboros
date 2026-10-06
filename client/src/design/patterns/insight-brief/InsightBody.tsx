"use client";

import { paragraphMentionsTag, type InsightParagraph } from "@/design/patterns/insight-brief/insight-utils";

type InsightBodyProps = {
  paragraphs: InsightParagraph[];
  activeTag: string | null;
  activePara: string | null;
  onSelectPara: (id: string) => void;
};

export function InsightBody({
  paragraphs,
  activeTag,
  activePara,
  onSelectPara,
}: InsightBodyProps) {
  return (
    <div className="ds-insight-body" role="list" aria-label="Insight body">
      {paragraphs.map((p, i) => {
        const lit = activeTag ? paragraphMentionsTag(p.text, activeTag) : false;
        const selected = p.id === activePara;
        return (
          <button
            key={p.id}
            type="button"
            role="listitem"
            className="ds-insight-body__para"
            style={{ animationDelay: `${i * 50}ms` }}
            data-lit={lit ? "true" : "false"}
            data-selected={selected ? "true" : "false"}
            data-tagging={activeTag ? "true" : "false"}
            aria-pressed={selected}
            onClick={() => onSelectPara(p.id)}
          >
            <span className="ds-insight-body__mark" aria-hidden />
            <span className="ds-insight-body__text">{p.text}</span>
          </button>
        );
      })}
    </div>
  );
}
