"use client";

import type { CSSProperties } from "react";
import { useEffect, useMemo, useState } from "react";

import { EventSensitivityAtmosphere } from "@/design/patterns/event-sensitivity/EventSensitivityAtmosphere";
import { EventSensitivityDial } from "@/design/patterns/event-sensitivity/EventSensitivityDial";
import { EventSensitivityFocus } from "@/design/patterns/event-sensitivity/EventSensitivityFocus";
import { EventSensitivityMast } from "@/design/patterns/event-sensitivity/EventSensitivityMast";
import { EventSensitivityRail } from "@/design/patterns/event-sensitivity/EventSensitivityRail";
import {
  buildEventRows,
  heatTone,
  measuredCount,
  rankEventRows,
} from "@/design/patterns/event-sensitivity/event-utils";
import { formatAsOfShort } from "@/design/patterns/profile/profile-utils";
import type { AssetProfile } from "@/lib/queries/asset-detail";

import "./event-sensitivity.css";

type EventSensitivityFieldProps = {
  profile: AssetProfile | null;
};

/**
 * Living event sensitivity plane — taxonomy + measured ATR multiples from profile.v1.
 * Full width under AssetSection; internal split keeps height in check.
 */
export function EventSensitivityField({ profile }: EventSensitivityFieldProps) {
  const rows = useMemo(
    () => rankEventRows(buildEventRows(profile?.event_sensitivities)),
    [profile],
  );
  const measured = useMemo(() => measuredCount(rows), [rows]);
  const lead = rows.find((r) => r.measured) ?? rows[0] ?? null;
  const [active, setActive] = useState<string | null>(null);

  useEffect(() => {
    if (!rows.length) {
      setActive(null);
      return;
    }
    if (!active || !rows.some((r) => r.event_type === active)) {
      setActive((lead ?? rows[0]).event_type);
    }
  }, [rows, active, lead]);

  const focus = rows.find((r) => r.event_type === active) ?? lead;
  const tone = heatTone(focus?.heat ?? "pending");

  if (!profile || rows.length === 0) {
    return (
      <section className="ds-event-field" aria-label="Event sensitivity">
        <div className="ds-event-field__rule" aria-hidden />
        <EventSensitivityAtmosphere />
        <div className="ds-event-field__empty">
          <h2>Event sensitivity</h2>
          <p>No event types mapped for this symbol yet. Rebuild daily profiles to land taxonomy.</p>
        </div>
      </section>
    );
  }

  return (
    <section
      className="ds-event-field"
      style={{ ["--ds-event-tone" as string]: tone } as CSSProperties}
      aria-label="Event sensitivity field"
    >
      <div className="ds-event-field__rule" aria-hidden />
      <EventSensitivityAtmosphere />
      <div className="ds-event-field__body">
        <EventSensitivityMast
          lead={lead}
          total={rows.length}
          measured={measured}
          stale={profile.provenance.stale}
        />
        <div className="ds-event-field__split">
          <EventSensitivityDial active={focus} />
          <EventSensitivityRail
            rows={rows}
            activeType={active}
            onSelect={setActive}
          />
        </div>
        <EventSensitivityFocus row={focus} />
        <p className="ds-event-field__foot">
          <span>{profile.provenance.model_version}</span>
          <span>as of {formatAsOfShort(profile.as_of)}</span>
          <span>post event H1 vs ATR · research only</span>
        </p>
      </div>
    </section>
  );
}
