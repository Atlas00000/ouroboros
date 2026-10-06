"use client";

import { useEffect, useId, useMemo, useState } from "react";

type DeskSignalFieldProps = {
  /** 0–1 progress hint for loading (optional). */
  pulse?: number;
  /** Visual tone for the primary path. */
  tone?: "signal" | "halt";
};

/**
 * Giant rotating desk instrument — rings + serpentine path.
 * Decorative; pointer wash lives on DeskStage.
 */
export function DeskSignalField({ pulse = 0.42, tone = "signal" }: DeskSignalFieldProps) {
  const gid = useId().replace(/:/g, "");
  const [reduceMotion, setReduceMotion] = useState(false);

  useEffect(() => {
    setReduceMotion(window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  }, []);

  const path = useMemo(
    () =>
      [
        "M 120 200",
        "C 120 110, 210 70, 280 95",
        "C 350 120, 360 200, 310 245",
        "C 260 290, 170 285, 140 230",
        "C 120 200, 150 160, 210 155",
        "C 270 150, 300 190, 275 220",
        "C 250 250, 200 245, 190 210",
      ].join(" "),
    [],
  );

  const ticks = useMemo(() => {
    const out: { x1: number; y1: number; x2: number; y2: number }[] = [];
    for (let i = 0; i < 24; i += 1) {
      const a = (i / 24) * Math.PI * 2;
      const outer = 168;
      const inner = i % 3 === 0 ? 148 : 156;
      out.push({
        x1: 200 + Math.cos(a) * inner,
        y1: 200 + Math.sin(a) * inner,
        x2: 200 + Math.cos(a) * outer,
        y2: 200 + Math.sin(a) * outer,
      });
    }
    return out;
  }, []);

  const orbitAngle = pulse * Math.PI * 2;
  const orbitR = 118;
  const ox = 200 + Math.cos(orbitAngle - Math.PI / 2) * orbitR;
  const oy = 200 + Math.sin(orbitAngle - Math.PI / 2) * orbitR;

  return (
    <div className="ds-desk-signal" aria-hidden>
      <svg
        className="ds-desk-signal__svg"
        viewBox="0 0 400 400"
        role="presentation"
      >
        <defs>
          <linearGradient id={`ds-sig-${gid}`} x1="0%" y1="0%" x2="100%" y2="100%">
            <stop
              offset="0%"
              stopColor={tone === "halt" ? "var(--ds-halt)" : "var(--ds-signal)"}
              stopOpacity="0.2"
            />
            <stop
              offset="55%"
              stopColor={tone === "halt" ? "var(--ds-halt)" : "var(--ds-signal)"}
              stopOpacity="1"
            />
            <stop
              offset="100%"
              stopColor="var(--ds-vol)"
              stopOpacity="0.65"
            />
          </linearGradient>
        </defs>

        <circle
          className="ds-desk-signal__ring"
          cx="200"
          cy="200"
          r="168"
          style={reduceMotion ? { animation: "none" } : undefined}
        />
        <circle
          className="ds-desk-signal__ring ds-desk-signal__ring--inner"
          cx="200"
          cy="200"
          r="128"
          style={reduceMotion ? { animation: "none" } : undefined}
        />

        {ticks.map((t, i) => (
          <line
            key={i}
            className="ds-desk-signal__tick"
            x1={t.x1}
            y1={t.y1}
            x2={t.x2}
            y2={t.y2}
          />
        ))}

        <path
          className="ds-desk-signal__path"
          d={path}
          stroke={`url(#ds-sig-${gid})`}
        />

        <circle className="ds-desk-signal__orbit" cx={ox} cy={oy} r="5.5" />
        <circle
          cx="200"
          cy="200"
          r="3"
          fill="var(--ds-ink-muted)"
          opacity="0.7"
        />
      </svg>
    </div>
  );
}
