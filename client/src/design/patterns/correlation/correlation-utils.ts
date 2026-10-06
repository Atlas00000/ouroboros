export type CorrPeer = {
  symbol: string;
  coefficient: number;
  window_days: number;
};

export type CorrPolarity = "sync" | "loose" | "diverge";

export type CorrBand = "tight" | "firm" | "soft";

export function corrPolarity(c: number): CorrPolarity {
  if (c >= 0.15) return "sync";
  if (c <= -0.15) return "diverge";
  return "loose";
}

export function corrBand(c: number): CorrBand {
  const a = Math.abs(c);
  if (a >= 0.7) return "tight";
  if (a >= 0.4) return "firm";
  return "soft";
}

export function corrPolarityLabel(p: CorrPolarity): string {
  if (p === "sync") return "Moves with";
  if (p === "diverge") return "Moves against";
  return "Near zero";
}

export function corrBandLabel(b: CorrBand): string {
  if (b === "tight") return "Tight link";
  if (b === "firm") return "Firm link";
  return "Soft link";
}

export function corrFocusBlurb(peer: CorrPeer): string {
  const p = corrPolarity(peer.coefficient);
  const b = corrBand(peer.coefficient);
  const win = peer.window_days;
  if (p === "sync") {
    return `${corrBandLabel(b)}. Rolling ${win}d co movement with this peer from profile.v1.`;
  }
  if (p === "diverge") {
    return `${corrBandLabel(b)}. Rolling ${win}d inverse posture versus this peer.`;
  }
  return `Loose coupling over ${win}d. Coefficient sits near the zero axis.`;
}

/** Sort by absolute strength; clamp display domain. */
export function rankCorrPeers(rows: CorrPeer[]): CorrPeer[] {
  return [...rows]
    .filter((r) => Number.isFinite(r.coefficient))
    .sort((a, b) => Math.abs(b.coefficient) - Math.abs(a.coefficient));
}

export function corrFieldBias(peers: CorrPeer[]): "sync" | "split" | "diverge" {
  if (!peers.length) return "split";
  let pos = 0;
  let neg = 0;
  for (const p of peers) {
    if (p.coefficient >= 0.15) pos += 1;
    else if (p.coefficient <= -0.15) neg += 1;
  }
  if (pos > neg + 1) return "sync";
  if (neg > pos + 1) return "diverge";
  return "split";
}

export function formatCoeff(c: number): string {
  const sign = c > 0 ? "+" : "";
  return `${sign}${c.toFixed(2)}`;
}

/** Map coefficient [-1,1] to percent along spectrum [0,100]. */
export function coeffToPct(c: number): number {
  const clamped = Math.max(-1, Math.min(1, c));
  return ((clamped + 1) / 2) * 100;
}

export function dominantWindow(peers: CorrPeer[]): number | null {
  if (!peers.length) return null;
  const counts = new Map<number, number>();
  for (const p of peers) {
    counts.set(p.window_days, (counts.get(p.window_days) ?? 0) + 1);
  }
  let best: number | null = null;
  let n = 0;
  for (const [days, count] of counts) {
    if (count > n) {
      best = days;
      n = count;
    }
  }
  return best;
}
