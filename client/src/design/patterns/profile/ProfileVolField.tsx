"use client";

import type { CSSProperties } from "react";

import { NumberTick } from "@/design/motion/NumberTick";
import type { ProfileMeter, ProfileMeterId } from "@/design/patterns/profile/profile-utils";

const R = 18;
const C = 2 * Math.PI * R;

type ProfileVolFieldProps = {
  meters: ProfileMeter[];
  active: ProfileMeterId;
  onSelect: (id: ProfileMeterId) => void;
};

function MeterButton({
  meter,
  active,
  onSelect,
}: {
  meter: ProfileMeter;
  active: boolean;
  onSelect: () => void;
}) {
  const clamped =
    meter.value == null || Number.isNaN(meter.value)
      ? null
      : Math.max(0, Math.min(100, meter.value));
  const hot = clamped != null && clamped >= 75;
  const offset = clamped == null ? C : C * (1 - clamped / 100);
  const center = clamped == null ? "—" : String(Math.round(clamped));

  return (
    <button
      type="button"
      className="ds-profile-meter"
      data-active={active ? "true" : "false"}
      data-hot={hot ? "true" : "false"}
      aria-pressed={active}
      onClick={onSelect}
    >
      <svg className="ds-profile-meter__svg" viewBox="0 0 44 44" aria-hidden>
        <circle className="ds-profile-meter__track" cx="22" cy="22" r={R} />
        <circle
          className="ds-profile-meter__value-arc"
          cx="22"
          cy="22"
          r={R}
          style={
            {
              strokeDasharray: C,
              strokeDashoffset: offset,
              "--ds-profile-meter-circ": String(C),
              "--ds-profile-meter-offset": String(offset),
            } as CSSProperties
          }
        />
        <text
          className="ds-profile-meter__center"
          x="22"
          y="22"
          textAnchor="middle"
          dominantBaseline="central"
        >
          {center}
        </text>
      </svg>
      <p className="ds-profile-meter__label">{meter.label}</p>
    </button>
  );
}

export function ProfileVolField({ meters, active, onSelect }: ProfileVolFieldProps) {
  const focus = meters.find((m) => m.id === active) ?? meters[0];
  const focusVal =
    focus?.value == null || Number.isNaN(focus.value) ? null : Math.round(focus.value);

  return (
    <div>
      <div className="ds-profile-dossier__meters" role="tablist" aria-label="Volatility meters">
        {meters.map((meter) => (
          <MeterButton
            key={meter.id}
            meter={meter}
            active={meter.id === active}
            onSelect={() => onSelect(meter.id)}
          />
        ))}
      </div>
      {focus ? (
        <div key={focus.id} className="ds-profile-dossier__focus" role="tabpanel">
          <p className="ds-profile-dossier__focus-value">
            <NumberTick value={focusVal} />
            <span className="ds-profile-dossier__focus-unit">{focus.unit}</span>
          </p>
          <p className="ds-profile-dossier__focus-copy">
            <strong>{focus.label}</strong>
            {focus.blurb}
          </p>
        </div>
      ) : null}
    </div>
  );
}
