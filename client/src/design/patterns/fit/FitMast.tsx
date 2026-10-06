import {
  familyLabel,
  FIT_TAG_COPY,
  formatRegimeLabel,
  type FitFamilyOption,
} from "@/design/patterns/fit/fit-utils";
import type { EdgeFamily, FitTag } from "@/lib/api/types";

type FitMastProps = {
  tag: FitTag;
  family: EdgeFamily;
  timeframe: string;
  regime?: string | null;
  allowOn: boolean;
  window?: string | null;
  stale?: boolean;
  families: FitFamilyOption[];
  onFamily: (family: EdgeFamily) => void;
  /** When true, family tabs are display-only (SSR seed without live fetch). */
  familyLocked?: boolean;
};

export function FitMast({
  tag,
  family,
  timeframe,
  regime,
  allowOn,
  window,
  stale,
  families,
  onFamily,
  familyLocked = false,
}: FitMastProps) {
  const copy = FIT_TAG_COPY[tag];

  return (
    <header className="ds-fit-field__mast">
      <div className="ds-fit-field__mast-lead">
        <p className="ds-fit-field__kicker">
          Regime fit
          {stale ? <span className="ds-fit-field__stale">stale</span> : null}
        </p>
        <h2 className="ds-fit-field__title" data-tag={tag}>
          {copy.label}
        </h2>
        <p className="ds-fit-field__lede">
          {familyLabel(family)} · {timeframe}
          {window ? ` · ${window} share` : null}
          {" · "}
          {formatRegimeLabel(regime)}
        </p>
      </div>
      <div className="ds-fit-field__mast-side">
        <div
          className="ds-fit-field__gate"
          data-on={allowOn ? "true" : "false"}
          title={allowOn ? "Research gate allow_on" : "Research gate off"}
        >
          <span className="ds-fit-field__gate-pulse" aria-hidden />
          <span className="ds-fit-field__gate-label">
            Gate {allowOn ? "on" : "off"}
          </span>
        </div>
        <div className="ds-fit-field__family" role="tablist" aria-label="Edge family">
          {families.map((f) => (
            <button
              key={f.id}
              type="button"
              role="tab"
              aria-selected={family === f.id}
              className="ds-fit-field__family-tab"
              data-active={family === f.id ? "true" : "false"}
              disabled={familyLocked && f.id !== family}
              onClick={() => {
                if (!familyLocked) onFamily(f.id);
              }}
            >
              {f.short}
            </button>
          ))}
        </div>
      </div>
    </header>
  );
}
