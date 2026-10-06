/** Desk hero stage model — Home herald for Ouroboros strengths. */

export const DESK_HERO_STAGES = ["regimes", "pricing", "news"] as const;

export type DeskHeroStageId = (typeof DESK_HERO_STAGES)[number];

export const DESK_HERO_DEFAULT: DeskHeroStageId = "regimes";

/** Auto-advance interval — calm desk pacing, not marketing carousel. */
export const DESK_HERO_DWELL_MS = 9000;

export const DESK_HERO_STAGE_META: Record<
  DeskHeroStageId,
  { label: string; eyebrow: string; blurb: string }
> = {
  regimes: {
    label: "Regimes",
    eyebrow: "Structure",
    blurb: "Living regime weight across the watchlist — research structure, not trade signals.",
  },
  pricing: {
    label: "Pricing",
    eyebrow: "Path",
    blurb: "Recent close paths for desk instruments — honesty over theatre.",
  },
  news: {
    label: "News",
    eyebrow: "Context",
    blurb: "High-impact narrative pressure feeding sentiment — context for sibling platforms.",
  },
};
