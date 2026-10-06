"use client";

import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type CSSProperties,
  type PointerEvent,
  type ReactNode,
} from "react";

import "./desk-stage.css";

type DeskStageProps = {
  children: ReactNode;
  className?: string;
  /** Accessible name for the stage landmark. */
  label: string;
};

/**
 * Full-bleed desk stage — pointer-reactive wash + ledger grid.
 * Hosts LoadingDesk / LostDesk compositions.
 */
export function DeskStage({ children, className, label }: DeskStageProps) {
  const rootRef = useRef<HTMLElement>(null);
  const [pos, setPos] = useState({ x: 18, y: 12 });
  const [reduceMotion, setReduceMotion] = useState(false);

  useEffect(() => {
    setReduceMotion(window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  }, []);

  const onMove = useCallback(
    (e: PointerEvent<HTMLElement>) => {
      if (reduceMotion) return;
      const el = rootRef.current;
      if (!el) return;
      const r = el.getBoundingClientRect();
      const x = ((e.clientX - r.left) / r.width) * 100;
      const y = ((e.clientY - r.top) / r.height) * 100;
      setPos({ x, y });
    },
    [reduceMotion],
  );

  const style = {
    ["--ds-stage-mx" as string]: `${pos.x}%`,
    ["--ds-stage-my" as string]: `${pos.y}%`,
  } as CSSProperties;

  return (
    <section
      ref={rootRef}
      className={["ds-desk-stage", className].filter(Boolean).join(" ")}
      aria-label={label}
      style={style}
      onPointerMove={onMove}
    >
      <div className="ds-desk-stage__wash" aria-hidden />
      <div className="ds-desk-stage__grid" aria-hidden />
      <div className="ds-desk-stage__sweep" aria-hidden />
      <div className="ds-desk-stage__frame">{children}</div>
    </section>
  );
}
