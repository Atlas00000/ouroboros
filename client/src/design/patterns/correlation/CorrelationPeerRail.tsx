"use client";

import { NumberTick } from "@/design/motion/NumberTick";
import {
  corrBand,
  corrPolarity,
  formatCoeff,
  type CorrPeer,
} from "@/design/patterns/correlation/correlation-utils";

type CorrelationPeerRailProps = {
  peers: CorrPeer[];
  activeSymbol: string | null;
  onSelect: (symbol: string) => void;
};

export function CorrelationPeerRail({
  peers,
  activeSymbol,
  onSelect,
}: CorrelationPeerRailProps) {
  return (
    <div className="ds-corr-rail" role="list" aria-label="Ranked peers">
      {peers.map((peer, i) => {
        const polarity = corrPolarity(peer.coefficient);
        const band = corrBand(peer.coefficient);
        const mag = Math.min(100, Math.abs(peer.coefficient) * 100);
        const active = peer.symbol === activeSymbol;
        return (
          <button
            key={peer.symbol}
            type="button"
            role="listitem"
            className="ds-corr-lane"
            style={{ animationDelay: `${i * 45}ms` }}
            data-polarity={polarity}
            data-band={band}
            data-active={active ? "true" : "false"}
            aria-pressed={active}
            onClick={() => onSelect(peer.symbol)}
          >
            <span className="ds-corr-lane__sym">{peer.symbol}</span>
            <span className="ds-corr-lane__bar" aria-hidden>
              <span
                className="ds-corr-lane__fill"
                style={{ width: `${mag}%` }}
              />
            </span>
            <span className="ds-corr-lane__val">
              <NumberTick value={formatCoeff(peer.coefficient)} />
            </span>
          </button>
        );
      })}
    </div>
  );
}
