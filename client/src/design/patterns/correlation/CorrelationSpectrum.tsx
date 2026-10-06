"use client";

import {
  coeffToPct,
  corrPolarity,
  formatCoeff,
  type CorrPeer,
} from "@/design/patterns/correlation/correlation-utils";

type CorrelationSpectrumProps = {
  peers: CorrPeer[];
  activeSymbol: string | null;
  onSelect: (symbol: string) => void;
};

export function CorrelationSpectrum({
  peers,
  activeSymbol,
  onSelect,
}: CorrelationSpectrumProps) {
  return (
    <div className="ds-corr-spectrum" role="list" aria-label="Correlation spectrum">
      <div className="ds-corr-spectrum__axis" aria-hidden>
        <span>−1</span>
        <span>0</span>
        <span>+1</span>
      </div>
      <div className="ds-corr-spectrum__track">
        <div className="ds-corr-spectrum__zero" aria-hidden />
        <div className="ds-corr-spectrum__glow ds-corr-spectrum__glow--neg" aria-hidden />
        <div className="ds-corr-spectrum__glow ds-corr-spectrum__glow--pos" aria-hidden />
        {peers.map((peer, i) => {
          const pct = coeffToPct(peer.coefficient);
          const polarity = corrPolarity(peer.coefficient);
          const active = peer.symbol === activeSymbol;
          return (
            <button
              key={peer.symbol}
              type="button"
              role="listitem"
              className="ds-corr-spectrum__mark"
              style={{
                left: `${pct}%`,
                animationDelay: `${i * 40}ms`,
              }}
              data-polarity={polarity}
              data-active={active ? "true" : "false"}
              aria-pressed={active}
              aria-label={`${peer.symbol} ${formatCoeff(peer.coefficient)}`}
              onClick={() => onSelect(peer.symbol)}
            >
              <span className="ds-corr-spectrum__pin" />
              <span className="ds-corr-spectrum__tag">{peer.symbol}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
