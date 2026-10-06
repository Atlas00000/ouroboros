"use client";

type FitFragileRailProps = {
  reasons: string[];
  active: string | null;
  onSelect: (reason: string | null) => void;
};

export function FitFragileRail({
  reasons,
  active,
  onSelect,
}: FitFragileRailProps) {
  if (!reasons.length) return null;

  return (
    <div className="ds-fit-fragile" aria-label="Fragile reasons">
      <p className="ds-fit-fragile__kicker">Fragile pressure</p>
      <ul className="ds-fit-fragile__rail">
        {reasons.map((reason, i) => {
          const selected = active === reason;
          return (
            <li key={`${reason}-${i}`}>
              <button
                type="button"
                className="ds-fit-fragile__chip"
                data-active={selected ? "true" : "false"}
                aria-pressed={selected}
                style={{ animationDelay: `${i * 40}ms` }}
                onClick={() => onSelect(selected ? null : reason)}
              >
                {reason.replaceAll("_", " ")}
              </button>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
