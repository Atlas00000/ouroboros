"use client";

type InsightTagRailProps = {
  tags: string[];
  activeTag: string | null;
  onSelect: (tag: string | null) => void;
};

export function InsightTagRail({ tags, activeTag, onSelect }: InsightTagRailProps) {
  if (!tags.length) return null;

  return (
    <div className="ds-insight-tags" role="list" aria-label="Insight tags">
      {tags.map((tag, i) => {
        const active = tag === activeTag;
        return (
          <button
            key={tag}
            type="button"
            role="listitem"
            className="ds-insight-tag"
            style={{ animationDelay: `${i * 40}ms` }}
            data-active={active ? "true" : "false"}
            aria-pressed={active}
            onClick={() => onSelect(active ? null : tag)}
          >
            {tag.replaceAll("_", " ")}
          </button>
        );
      })}
    </div>
  );
}
