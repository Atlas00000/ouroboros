import { Text } from "@/design/primitives/Text";

/** Live mark — CSS signal only, never emoji or illustration. */
export function PulseLiveMark() {
  return (
    <div className="ds-pulse-live" aria-live="polite">
      <span className="ds-pulse-live__ring" aria-hidden>
        <span className="ds-pulse-live__core" />
      </span>
      <Text as="span" variant="label" className="ds-pulse-live__label">
        Desk live
      </Text>
    </div>
  );
}
