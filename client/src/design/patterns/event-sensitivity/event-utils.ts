export type EventSenseRow = {
  event_type: string;
  label: string;
  atr: number | null;
  measured: boolean;
  notes: string | null;
  heat: "hot" | "warm" | "calm" | "pending";
};

const LABELS: Record<string, string> = {
  NFP: "Nonfarm payrolls",
  CPI: "Consumer prices",
  FOMC: "Fed decision",
  GDP: "Growth print",
  central_bank: "Central bank",
};

export function eventLabel(eventType: string): string {
  return LABELS[eventType] ?? eventType.replaceAll("_", " ");
}

export function eventHeat(atr: number | null): EventSenseRow["heat"] {
  if (atr == null || Number.isNaN(atr)) return "pending";
  if (atr >= 2) return "hot";
  if (atr >= 1) return "warm";
  return "calm";
}

export function buildEventRows(
  rows:
    | {
        event_type: string;
        typical_move_atr_multiple?: number | null;
        notes?: string | null;
      }[]
    | undefined
    | null,
): EventSenseRow[] {
  if (!rows?.length) return [];
  return rows.map((r) => {
    const atr =
      r.typical_move_atr_multiple == null || Number.isNaN(r.typical_move_atr_multiple)
        ? null
        : r.typical_move_atr_multiple;
    return {
      event_type: r.event_type,
      label: eventLabel(r.event_type),
      atr,
      measured: atr != null,
      notes: r.notes?.trim() || null,
      heat: eventHeat(atr),
    };
  });
}

/** Rank measured first by ATR desc, then pending by label. */
export function rankEventRows(rows: EventSenseRow[]): EventSenseRow[] {
  return [...rows].sort((a, b) => {
    if (a.measured !== b.measured) return a.measured ? -1 : 1;
    if (a.atr != null && b.atr != null) return b.atr - a.atr;
    return a.event_type.localeCompare(b.event_type);
  });
}

export function formatAtr(atr: number | null): string {
  if (atr == null) return "n/a";
  return `${atr.toFixed(2)}×`;
}

/** Map ATR multiple onto 0–100 dial (cap at 3×). */
export function atrToPct(atr: number | null): number {
  if (atr == null || Number.isNaN(atr)) return 0;
  return Math.max(0, Math.min(100, (atr / 3) * 100));
}

export function heatTone(heat: EventSenseRow["heat"]): string {
  if (heat === "hot") return "var(--ds-vol)";
  if (heat === "warm") return "var(--ds-warn)";
  if (heat === "calm") return "var(--ds-signal)";
  return "var(--ds-idle)";
}

export function heatLabel(heat: EventSenseRow["heat"]): string {
  if (heat === "hot") return "Sharp print";
  if (heat === "warm") return "Material move";
  if (heat === "calm") return "Contained move";
  return "Awaiting samples";
}

export function eventFocusBlurb(row: EventSenseRow): string {
  if (row.notes) return row.notes;
  if (row.measured) {
    return `Typical post event H1 range sits near ${formatAtr(row.atr)} ATR for ${row.label}.`;
  }
  return `${row.label} is on the taxonomy for this symbol. ATR multiple lands when enough calendar samples clear the gate.`;
}

export function measuredCount(rows: EventSenseRow[]): number {
  return rows.filter((r) => r.measured).length;
}
