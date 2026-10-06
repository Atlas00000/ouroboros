import {
  FIT_TAG_COPY,
  formatRegimeLabel,
  formatSharePct,
  type FitShareRow,
} from "@/design/patterns/fit/fit-utils";
import type { FitTag } from "@/lib/api/types";

type FitFocusProps = {
  liveTag: FitTag;
  focusTag: FitTag | null;
  focusShare: FitShareRow | null;
  regime?: string | null;
  allowOn: boolean;
  fragileReason: string | null;
  disclaimer?: string | null;
};

export function FitFocus({
  liveTag,
  focusTag,
  focusShare,
  regime,
  allowOn,
  fragileReason,
  disclaimer,
}: FitFocusProps) {
  const tag = focusTag ?? liveTag;
  const copy = FIT_TAG_COPY[tag];
  const isLive = tag === liveTag;

  return (
    <aside className="ds-fit-focus" aria-live="polite">
      <p className="ds-fit-focus__kicker">
        {fragileReason ? "Fragile reason" : isLive ? "Live gate" : "Share probe"}
      </p>
      <h3 className="ds-fit-focus__title" data-tag={tag}>
        {fragileReason ? fragileReason.replaceAll("_", " ") : copy.label}
      </h3>
      <p className="ds-fit-focus__body">
        {fragileReason
          ? "Calendar or vol overlay flagged FRAGILE for this cut. Research size or pause — not an execution block by itself."
          : copy.blurb}
      </p>
      <dl className="ds-fit-focus__metrics">
        <div>
          <dt>Regime</dt>
          <dd>{formatRegimeLabel(regime)}</dd>
        </div>
        <div>
          <dt>Window share</dt>
          <dd>
            {focusShare && focusShare.share > 0
              ? formatSharePct(focusShare.share)
              : "—"}
          </dd>
        </div>
        <div>
          <dt>Gate</dt>
          <dd>{allowOn ? "allow on" : "off"}</dd>
        </div>
      </dl>
      {disclaimer ? (
        <p className="ds-fit-focus__disclaimer">{disclaimer}</p>
      ) : null}
    </aside>
  );
}
