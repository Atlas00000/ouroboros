"use client";

import { useAuth } from "@clerk/nextjs";
import { useQuery } from "@tanstack/react-query";

import { FitTagChip } from "@/design/patterns/fit/FitTagChip";
import { fetchApi } from "@/lib/api/client";
import type { FitSnapshot } from "@/lib/api/types";

const clerkEnabled = Boolean(process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY);

type Props = {
  symbol?: string | null;
};

function FitHeroChipLive({ symbol }: { symbol: string }) {
  const { getToken, isLoaded } = useAuth();
  const q = useQuery({
    queryKey: ["fit-hero", symbol],
    enabled: isLoaded && Boolean(symbol),
    queryFn: async () => {
      const token = await getToken();
      const params = new URLSearchParams({
        symbol,
        family: "meanrev",
        timeframe: "H1",
      });
      try {
        return await fetchApi<FitSnapshot>(`/v1/fit?${params}`, { token });
      } catch {
        return null;
      }
    },
  });

  if (!q.data) return null;
  return <FitTagChip tag={q.data.tag} allowOn={q.data.allow_on} />;
}

/** Single-symbol fit chip for DeskHero — only mounts under ClerkProvider when enabled. */
export function FitHeroChip({ symbol }: Props) {
  if (!clerkEnabled || !symbol) return null;
  return <FitHeroChipLive symbol={symbol} />;
}
