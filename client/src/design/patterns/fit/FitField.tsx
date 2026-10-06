"use client";

import { useAuth } from "@clerk/nextjs";
import { useQuery } from "@tanstack/react-query";
import type { CSSProperties } from "react";
import { useEffect, useMemo, useState } from "react";

import { FitAtmosphere } from "@/design/patterns/fit/FitAtmosphere";
import { FitFocus } from "@/design/patterns/fit/FitFocus";
import { FitFragileRail } from "@/design/patterns/fit/FitFragileRail";
import { FitMast } from "@/design/patterns/fit/FitMast";
import { FitShareRibbon } from "@/design/patterns/fit/FitShareRibbon";
import { FitTagStage } from "@/design/patterns/fit/FitTagStage";
import {
  buildShareRows,
  FIT_FAMILIES,
  fitToneCss,
} from "@/design/patterns/fit/fit-utils";
import { formatAsOfShort } from "@/design/patterns/profile/profile-utils";
import { fetchApi } from "@/lib/api/client";
import type { EdgeFamily, FitSnapshot, FitTag } from "@/lib/api/types";

import "./fit-field.css";

const clerkEnabled = Boolean(process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY);

type FitFieldProps = {
  symbol: string;
  /** Optional SSR seed for meanrev H1+30d. */
  initial?: FitSnapshot | null;
};

async function loadFit(
  symbol: string,
  family: EdgeFamily,
  token: string | null,
): Promise<FitSnapshot | null> {
  const q = new URLSearchParams({
    symbol,
    family,
    timeframe: "H1",
    window: "30d",
  });
  try {
    return await fetchApi<FitSnapshot>(`/v1/fit?${q}`, {
      token: token ?? undefined,
    });
  } catch {
    return null;
  }
}

function FitFieldEmpty({ message }: { message: string }) {
  return (
    <section className="ds-fit-field" data-tag="idle" aria-label="Regime fit">
      <div className="ds-fit-field__rule" aria-hidden />
      <FitAtmosphere />
      <div className="ds-fit-field__empty">
        <h2>Regime fit</h2>
        <p>{message}</p>
      </div>
    </section>
  );
}

function FitFieldPlane({
  snap,
  family,
  onFamily,
  loading,
  familyLocked = false,
}: {
  snap: FitSnapshot;
  family: EdgeFamily;
  onFamily: (f: EdgeFamily) => void;
  loading?: boolean;
  familyLocked?: boolean;
}) {
  const rows = useMemo(() => buildShareRows(snap.shares), [snap.shares]);
  const [activeTag, setActiveTag] = useState<FitTag | null>(snap.tag);
  const [fragileReason, setFragileReason] = useState<string | null>(null);

  useEffect(() => {
    setActiveTag(snap.tag);
    setFragileReason(null);
  }, [snap.as_of, snap.tag, snap.family]);

  const focusShare = rows.find((r) => r.tag === activeTag) ?? null;
  const tone = fitToneCss(snap.tag);

  return (
    <section
      className="ds-fit-field"
      data-tag={snap.tag}
      data-gate={snap.allow_on ? "on" : "off"}
      data-loading={loading ? "true" : "false"}
      style={{ ["--ds-fit-tone" as string]: tone } as CSSProperties}
      aria-label="Regime fit field"
    >
      <div className="ds-fit-field__rule" aria-hidden />
      <FitAtmosphere />
      <div className="ds-fit-field__body">
        <FitMast
          tag={snap.tag}
          family={family}
          timeframe={snap.timeframe}
          regime={snap.regime}
          allowOn={snap.allow_on}
          window={snap.window}
          stale={snap.provenance.stale}
          families={FIT_FAMILIES}
          onFamily={onFamily}
          familyLocked={familyLocked}
        />
        <div className="ds-fit-field__split">
          <FitTagStage
            liveTag={snap.tag}
            rows={rows}
            activeTag={activeTag}
            onSelect={(tag) => {
              setFragileReason(null);
              setActiveTag(tag);
            }}
          />
          <FitFocus
            liveTag={snap.tag}
            focusTag={activeTag}
            focusShare={focusShare}
            regime={snap.regime}
            allowOn={snap.allow_on}
            fragileReason={fragileReason}
            disclaimer={snap.disclaimer?.text}
          />
        </div>
        <FitShareRibbon
          rows={rows}
          activeTag={activeTag}
          window={snap.window}
          onSelect={(tag) => {
            setFragileReason(null);
            setActiveTag(tag);
          }}
        />
        <FitFragileRail
          reasons={snap.fragile_reasons ?? []}
          active={fragileReason}
          onSelect={setFragileReason}
        />
        <p className="ds-fit-field__foot">
          <span>{snap.provenance.model_version}</span>
          <span>as of {formatAsOfShort(snap.as_of)}</span>
          <span>research gate · not execution</span>
        </p>
      </div>
    </section>
  );
}

function FitFieldLive({ symbol, initial }: FitFieldProps) {
  const { getToken, isLoaded } = useAuth();
  const [family, setFamily] = useState<EdgeFamily>(initial?.family ?? "meanrev");

  const q = useQuery({
    queryKey: ["fit", symbol, family],
    enabled: isLoaded,
    initialData: family === initial?.family ? (initial ?? undefined) : undefined,
    queryFn: async () => {
      const token = await getToken();
      return loadFit(symbol, family, token);
    },
  });

  const snap = q.data ?? null;

  if (q.isError && !snap) {
    return <FitFieldEmpty message="Fit unavailable for this symbol." />;
  }
  if (q.isLoading && !snap) {
    return <FitFieldEmpty message="Loading fit…" />;
  }
  if (!snap) {
    return <FitFieldEmpty message="No fit snapshot for this cut yet." />;
  }

  return (
    <FitFieldPlane
      snap={snap}
      family={family}
      onFamily={setFamily}
      loading={q.isFetching && !q.isLoading}
    />
  );
}

/**
 * Living regime-fit plane — fit.v1 tag + shares + gate for edge family × TF.
 * Full width under AssetSection; capped height, not oversized.
 */
export function FitField({ symbol, initial }: FitFieldProps) {
  if (!clerkEnabled) {
    if (!initial) {
      return (
        <FitFieldEmpty message="No seeded fit snapshot. Configure Clerk or pass SSR fit." />
      );
    }
    return (
      <FitFieldPlane
        snap={initial}
        family={initial.family}
        onFamily={() => undefined}
        familyLocked
      />
    );
  }
  return <FitFieldLive symbol={symbol} initial={initial} />;
}
