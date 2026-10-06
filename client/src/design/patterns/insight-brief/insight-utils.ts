import type { Insight } from "@/lib/queries/asset-detail";

export type InsightParagraph = {
  id: string;
  text: string;
};

export function splitInsightBody(body: string): InsightParagraph[] {
  const chunks = body
    .split(/\n+/)
    .map((s) => s.trim())
    .filter(Boolean);
  if (!chunks.length && body.trim()) {
    return [{ id: "p0", text: body.trim() }];
  }
  return chunks.map((text, i) => ({ id: `p${i}`, text }));
}

export function normalizeTags(tags: string[] | undefined | null): string[] {
  if (!tags?.length) return [];
  return tags.map((t) => t.trim()).filter(Boolean);
}

export function normalizeRefs(refs: string[] | undefined | null): string[] {
  if (!refs?.length) return [];
  return refs.map((r) => r.trim()).filter(Boolean);
}

export function insightTypeLabel(type: string | undefined | null): string {
  const t = (type || "narrative").toLowerCase();
  if (t === "narrative") return "Narrative";
  return t.replaceAll("_", " ");
}

export function paragraphMentionsTag(text: string, tag: string): boolean {
  const needle = tag.trim().toLowerCase().replaceAll("_", " ");
  if (!needle) return false;
  const hay = text.toLowerCase();
  if (hay.includes(needle)) return true;
  const compact = needle.replace(/\s+/g, "");
  return hay.replace(/[\s_-]+/g, "").includes(compact);
}

export function defaultDisclaimer(text?: string | null): string {
  return (
    text?.trim() ||
    "Internal research context only. Outputs are not investment advice and do not execute trades."
  );
}

export function insightFocusBlurb(
  insight: Insight,
  activeTag: string | null,
): string {
  if (activeTag) {
    return `Tag ${activeTag.replaceAll("_", " ")} staged against the narrative body. Research context only.`;
  }
  const n = insight.tags?.length ?? 0;
  const r = insight.related_refs?.length ?? 0;
  return `Labeled ${insightTypeLabel(insight.type)} brief · ${n} tags · ${r} related refs. Read beside the numbers above, never as a trade ticket.`;
}
