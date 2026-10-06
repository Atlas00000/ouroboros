import { cssVarForTone, toneForRegime, type Regime } from "@/design/map/backend-visual";

type UniverseAtmosphereProps = {
  focusRegime?: string | null;
};

/** Quiet stage wash — token gradients only, no illustration. */
export function UniverseAtmosphere({ focusRegime }: UniverseAtmosphereProps) {
  const tone = cssVarForTone(toneForRegime(focusRegime as Regime));

  return (
    <div
      className="ds-universe__atmosphere"
      style={{ ["--ds-universe-focus" as string]: tone }}
      aria-hidden
    />
  );
}
