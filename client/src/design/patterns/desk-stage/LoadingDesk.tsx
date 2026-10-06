"use client";

import { useEffect, useState } from "react";

import { DeskSignalField } from "@/design/patterns/desk-stage/DeskSignalField";
import { DeskStage } from "@/design/patterns/desk-stage/DeskStage";

const PHASES = [
  "Opening ledger",
  "Syncing watchlist",
  "Warming price paths",
  "Staging narrative cut",
] as const;

/**
 * Full-bleed loading desk — brand-forward, instrument field, sweeping signal.
 */
export function LoadingDesk() {
  const [phase, setPhase] = useState(0);
  const [pulse, setPulse] = useState(0.15);

  useEffect(() => {
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce) return;

    const phaseId = window.setInterval(() => {
      setPhase((p) => (p + 1) % PHASES.length);
    }, 1600);

    const pulseId = window.setInterval(() => {
      setPulse((p) => (p + 0.035) % 1);
    }, 80);

    return () => {
      window.clearInterval(phaseId);
      window.clearInterval(pulseId);
    };
  }, []);

  return (
    <DeskStage label="Loading Ouroboros desk">
      <DeskSignalField pulse={pulse} />

      <header className="ds-desk-stage__mast">
        <p className="ds-desk-stage__eyebrow">Research desk · live cut</p>
        <h1 className="ds-desk-stage__title">Ouroboros</h1>
        <p className="ds-desk-stage__lede">
          Staging living asset profiles — price paths, regimes, and narrative
          pressure on one ledger. Hold for the session cut.
        </p>
      </header>

      <div className="ds-desk-loadbar" role="status" aria-live="polite">
        <div className="ds-desk-loadbar__track" aria-hidden>
          <div className="ds-desk-loadbar__fill" />
        </div>
        <div className="ds-desk-loadbar__meta">
          <span>
            Phase <strong>{String(phase + 1).padStart(2, "0")}</strong> / 04
          </span>
          <span>{PHASES[phase]}</span>
        </div>
      </div>
    </DeskStage>
  );
}
