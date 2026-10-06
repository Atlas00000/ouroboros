import {
  cssVarForTone,
  type SemanticTone,
} from "@/design/map/backend-visual";

/** Resolve a CSS custom property to a concrete color string (client only). */
export function readCssVar(name: string, fallback = ""): string {
  if (typeof window === "undefined") return fallback;
  const value = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  return value || fallback;
}

export type ChartTheme = {
  ink: string;
  inkMuted: string;
  line: string;
  lineStrong: string;
  plane: string;
  planeRaised: string;
  canvas: string;
  signal: string;
  ok: string;
  halt: string;
  warn: string;
  vol: string;
  idle: string;
};

export function readChartTheme(): ChartTheme {
  return {
    ink: readCssVar("--ds-ink", "#e4ebe6"),
    inkMuted: readCssVar("--ds-ink-muted", "#85948c"),
    line: readCssVar("--ds-line", "#1c2621"),
    lineStrong: readCssVar("--ds-line-strong", "#2a3630"),
    plane: readCssVar("--ds-plane", "#111614"),
    planeRaised: readCssVar("--ds-plane-raised", "#171d1a"),
    canvas: readCssVar("--ds-canvas", "#090c0b"),
    signal: readCssVar("--ds-signal", "#5f9e86"),
    ok: readCssVar("--ds-ok", "#5f9e86"),
    halt: readCssVar("--ds-halt", "#b56a62"),
    warn: readCssVar("--ds-warn", "#b8934e"),
    vol: readCssVar("--ds-vol", "#b8934e"),
    idle: readCssVar("--ds-idle", "#85948c"),
  };
}

export function colorForTone(tone: SemanticTone, theme?: ChartTheme): string {
  const t = theme ?? readChartTheme();
  switch (tone) {
    case "signal":
      return t.signal;
    case "ok":
      return t.ok;
    case "halt":
      return t.halt;
    case "warn":
      return t.warn;
    case "vol":
      return t.vol;
    case "idle":
      return t.idle;
    case "faint":
    default:
      return t.inkMuted;
  }
}

/** Prefer CSS var string for SVG attributes that resolve at paint time. */
export function cssVarStroke(tone: SemanticTone): string {
  return cssVarForTone(tone);
}

export function prefersReducedMotion(): boolean {
  if (typeof window === "undefined") return false;
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}
