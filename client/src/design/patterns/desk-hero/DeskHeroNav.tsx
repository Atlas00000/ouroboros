"use client";

import {
  DESK_HERO_STAGES,
  DESK_HERO_STAGE_META,
  type DeskHeroStageId,
} from "@/design/patterns/desk-hero/types";
import { cn } from "@/lib/utils";

type DeskHeroNavProps = {
  value: DeskHeroStageId;
  onChange: (stage: DeskHeroStageId) => void;
  progress: number;
};

/** Typography stage rail — not Bootstrap tabs or carousel dots. */
export function DeskHeroNav({ value, onChange, progress }: DeskHeroNavProps) {
  return (
    <div className="ds-desk-hero__nav">
      <div className="ds-desk-hero__nav-tabs" role="tablist" aria-label="Desk hero stages">
        {DESK_HERO_STAGES.map((id) => {
          const active = value === id;
          return (
            <button
              key={id}
              type="button"
              role="tab"
              aria-selected={active}
              id={`desk-hero-tab-${id}`}
              className={cn("ds-desk-hero__tab", active && "is-active")}
              onClick={() => onChange(id)}
            >
              <span className="ds-desk-hero__tab-eyebrow">
                {DESK_HERO_STAGE_META[id].eyebrow}
              </span>
              <span className="ds-desk-hero__tab-label">
                {DESK_HERO_STAGE_META[id].label}
              </span>
            </button>
          );
        })}
      </div>
      <div
        className="ds-desk-hero__progress"
        role="presentation"
        aria-hidden
      >
        <span
          className="ds-desk-hero__progress-fill"
          style={{ transform: `scaleX(${Math.min(1, Math.max(0, progress))})` }}
        />
      </div>
    </div>
  );
}
