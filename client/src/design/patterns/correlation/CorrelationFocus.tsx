"use client";

import { NumberTick } from "@/design/motion/NumberTick";
import {
  corrBand,
  corrBandLabel,
  corrFocusBlurb,
  corrPolarity,
  corrPolarityLabel,
  formatCoeff,
  type CorrPeer,
} from "@/design/patterns/correlation/correlation-utils";

type CorrelationFocusProps = {
  peer: CorrPeer | null;
};

export function CorrelationFocus({ peer }: CorrelationFocusProps) {
  if (!peer) return null;

  const polarity = corrPolarity(peer.coefficient);
  const band = corrBand(peer.coefficient);

  return (
    <div
      key={peer.symbol}
      className="ds-corr-focus"
      data-polarity={polarity}
      role="status"
    >
      <p className="ds-corr-focus__value">
        <NumberTick value={formatCoeff(peer.coefficient)} />
      </p>
      <div className="ds-corr-focus__copy">
        <strong>
          {peer.symbol} · {corrPolarityLabel(polarity)} · {corrBandLabel(band)}
        </strong>
        <span>{corrFocusBlurb(peer)}</span>
      </div>
    </div>
  );
}
