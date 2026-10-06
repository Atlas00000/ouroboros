"use client";

import type { CSSProperties } from "react";

import {
  FIT_TAG_COPY,
  type FitShareRow,
} from "@/design/patterns/fit/fit-utils";
import type { FitTag } from "@/lib/api/types";

type FitTagStageProps = {
  liveTag: FitTag;
  rows: FitShareRow[];
  activeTag: FitTag | null;
  onSelect: (tag: FitTag) => void;
};

/** Triad stage — live tag dominates; click probes share tags. */
export function FitTagStage({
  liveTag,
  rows,
  activeTag,
  onSelect,
}: FitTagStageProps) {
  return (
    <div className="ds-fit-stage" role="list" aria-label="Fit tag stage">
      {rows.map((row, i) => {
        const live = row.tag === liveTag;
        const active = row.tag === activeTag;
        const copy = FIT_TAG_COPY[row.tag];
        return (
          <button
            key={row.tag}
            type="button"
            role="listitem"
            className="ds-fit-stage__cell"
            style={
              {
                ["--ds-fit-cell" as string]: row.color,
                animationDelay: `${i * 60}ms`,
              } as CSSProperties
            }
            data-live={live ? "true" : "false"}
            data-active={active ? "true" : "false"}
            aria-pressed={active}
            aria-label={`${copy.label}${live ? ", live tag" : ""}`}
            onClick={() => onSelect(row.tag)}
          >
            <span className="ds-fit-stage__glow" aria-hidden />
            <span className="ds-fit-stage__name">{copy.label}</span>
            <span className="ds-fit-stage__pct">
              {row.pct > 0 ? `${row.pct}%` : "—"}
            </span>
            {live ? <span className="ds-fit-stage__live">live</span> : null}
          </button>
        );
      })}
    </div>
  );
}
