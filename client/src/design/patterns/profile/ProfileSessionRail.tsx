"use client";

import { useEffect, useMemo, useState } from "react";

import {
  formatProfileTime,
  sessionIsLiveUtc,
} from "@/design/patterns/profile/profile-utils";
import type { AssetProfile } from "@/lib/queries/asset-detail";

type ProfileSessionRailProps = {
  profile: AssetProfile;
};

export function ProfileSessionRail({ profile }: ProfileSessionRailProps) {
  const hours = profile.trading_hours;
  const sessions = hours?.sessions ?? [];
  const [utcHour, setUtcHour] = useState(() => new Date().getUTCHours());
  const [utcMinute, setUtcMinute] = useState(() => new Date().getUTCMinutes());
  const [utcClock, setUtcClock] = useState(() => {
    const n = new Date();
    return `${String(n.getUTCHours()).padStart(2, "0")}:${String(n.getUTCMinutes()).padStart(2, "0")}`;
  });
  const [selected, setSelected] = useState<string | null>(null);

  useEffect(() => {
    const tick = () => {
      const n = new Date();
      setUtcHour(n.getUTCHours());
      setUtcMinute(n.getUTCMinutes());
      setUtcClock(
        `${String(n.getUTCHours()).padStart(2, "0")}:${String(n.getUTCMinutes()).padStart(2, "0")}`,
      );
    };
    tick();
    const id = window.setInterval(tick, 30_000);
    return () => window.clearInterval(id);
  }, []);

  const liveSet = useMemo(() => {
    const set = new Set<string>();
    for (const s of sessions) {
      if (sessionIsLiveUtc(s, utcHour)) set.add(s);
    }
    return set;
  }, [sessions, utcHour]);

  useEffect(() => {
    if (selected) return;
    const firstLive = sessions.find((s) => liveSet.has(s));
    if (firstLive) setSelected(firstLive);
    else if (sessions[0]) setSelected(sessions[0]);
  }, [sessions, liveSet, selected]);

  if (!hours || sessions.length === 0) return null;

  const open = formatProfileTime(hours.open_utc);
  const close = formatProfileTime(hours.close_utc);
  const selectedLive = selected ? liveSet.has(selected) : false;
  const needlePct = ((utcHour * 60 + utcMinute) / (24 * 60)) * 100;

  return (
    <div className="ds-profile-sessions">
      <div className="ds-profile-sessions__head">
        <h3 className="ds-profile-sessions__title">Sessions</h3>
        <p className="ds-profile-sessions__clock">
          {utcClock} UTC
          {hours.timezone ? ` · ${hours.timezone}` : ""}
          {open && close ? ` · desk ${open}→${close}` : ""}
        </p>
      </div>
      <div className="ds-profile-sessions__ribbon" aria-hidden>
        <span className="ds-profile-sessions__needle" style={{ left: `${needlePct}%` }} />
      </div>
      <div className="ds-profile-sessions__rail" role="list">
        {sessions.map((name) => {
          const live = liveSet.has(name);
          return (
            <button
              key={name}
              type="button"
              className="ds-profile-session"
              role="listitem"
              data-live={live ? "true" : "false"}
              data-selected={selected === name ? "true" : "false"}
              aria-pressed={selected === name}
              onClick={() => setSelected(name)}
            >
              <span className="ds-profile-session__row">
                {live ? (
                  <span className="ds-profile-session__pulse" aria-hidden>
                    <span className="ds-profile-session__pulse-core" />
                    <span className="ds-profile-session__pulse-ring" />
                  </span>
                ) : null}
                <span className="ds-profile-session__name">{name.replaceAll("_", " ")}</span>
              </span>
              <span className="ds-profile-session__state">{live ? "Live" : "Closed"}</span>
            </button>
          );
        })}
      </div>
      <p className="ds-profile-dossier__focus-copy">
        <strong>{selected?.replaceAll("_", " ") ?? "Session"}</strong>
        {selectedLive
          ? "Approximate session window is open vs UTC wall clock."
          : hours.notes?.trim() ||
            "Approximate session window — broker cash hours may differ."}
      </p>
    </div>
  );
}
