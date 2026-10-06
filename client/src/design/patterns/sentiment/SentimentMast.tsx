import { StaleBadge } from "@/components/StaleBadge";
import { NumberTick } from "@/design/motion/NumberTick";
import {
  formatScore,
  polarityLabel,
  type SentimentPolarity,
} from "@/design/patterns/sentiment/sentiment-utils";

type SentimentMastProps = {
  score: number;
  polarity: SentimentPolarity;
  itemCount: number;
  windowHours: number;
  stale?: boolean;
};

export function SentimentMast({
  score,
  polarity,
  itemCount,
  windowHours,
  stale,
}: SentimentMastProps) {
  return (
    <header className="ds-sent-field__mast">
      <p className="ds-sent-field__kicker">
        <span>Sentiment</span>
        <StaleBadge stale={stale} />
        <span>
          {itemCount} items · {windowHours}h
        </span>
      </p>
      <p className="ds-sent-field__score">
        <NumberTick value={formatScore(score)} />
      </p>
      <p className="ds-sent-field__badge">{polarityLabel(polarity)}</p>
      <p className="ds-sent-field__meta">
        Decay weighted aggregate from scored headlines in the live window.
      </p>
    </header>
  );
}
