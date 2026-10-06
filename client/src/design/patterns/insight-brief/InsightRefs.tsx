type InsightRefsProps = {
  refs: string[];
};

export function InsightRefs({ refs }: InsightRefsProps) {
  if (!refs.length) return null;

  return (
    <div className="ds-insight-refs" aria-label="Related refs">
      <p className="ds-insight-refs__label">Related refs</p>
      <ul className="ds-insight-refs__list">
        {refs.map((ref) => (
          <li key={ref} className="ds-insight-refs__item">
            <span className="font-[family-name:var(--ds-font-numeric)]">{ref}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
