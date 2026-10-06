import Link from "next/link";

import { StateBadge } from "@/components/StateBadge";
import { StaleBadge } from "@/components/StaleBadge";
import { ASSET_COPY } from "@/design/patterns/asset-copy";
import { AssetSection } from "@/design/patterns/AssetSection";
import { CorrelationField } from "@/design/patterns/correlation";
import { DriverPress } from "@/design/patterns/driver-press";
import { FitField } from "@/design/patterns/fit";
import { InsightBrief } from "@/design/patterns/insight-brief";
import { EventSensitivityField, ProfileDossier } from "@/design/patterns/profile";
import { PriceRegimeChart } from "@/design/patterns/price-regime";
import { SectionWrap } from "@/design/patterns/SectionWrap";
import { SentimentField } from "@/design/patterns/sentiment";
import {
  RegimeHistoryField,
  RegimeNowcastField,
} from "@/design/patterns/state";
import { AppShell } from "@/design/shells/AppShell";
import { Text } from "@/design/primitives/Text";
import { fetchAssetDetailServer } from "@/lib/queries/asset-detail";
import { fetchFitServer } from "@/lib/queries/server";

type Props = { params: Promise<{ symbol: string }> };

export const dynamic = "force-dynamic";

export default async function AssetDetailPage({ params }: Props) {
  const { symbol } = await params;
  const detail = await fetchAssetDetailServer(symbol);
  const sym = detail.symbol;
  const fitSeed = await fetchFitServer(sym, "meanrev", "H1", "30d");
  const anyStale = Boolean(
    detail.bars?.provenance.stale ||
      detail.state?.provenance.stale ||
      detail.profile?.provenance.stale ||
      detail.sentiment?.provenance.stale ||
      detail.insight?.provenance.stale,
  );

  return (
    <AppShell wide>
      <div className="sticky top-0 z-10 -mx-4 mb-6 border-b border-ds-line bg-ds-canvas/95 px-4 py-3 backdrop-blur sm:-mx-6 sm:px-6 lg:-mx-8 lg:px-8">
        <Link
          href="/"
          className="text-xs text-ds-ink-muted hover:text-ds-ink focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ds-signal"
        >
          ← Home
        </Link>
        <div className="mt-2 flex flex-wrap items-center gap-3">
          <Text as="h1" variant="title" className="font-mono tracking-tight">
            {sym}
          </Text>
          <StateBadge regime={detail.state?.regime} />
          <StaleBadge stale={anyStale} />
          {detail.profile?.identity.display_name ? (
            <Text as="span" variant="muted" className="text-[length:var(--ds-text-label)]">
              {detail.profile.identity.display_name}
            </Text>
          ) : null}
        </div>
        <div className="mt-2 max-w-2xl">
          <SectionWrap eyebrow={ASSET_COPY.mast.eyebrow}>
            {ASSET_COPY.mast.wrap}
          </SectionWrap>
        </div>
      </div>

      <div className="flex flex-col gap-8">
        <AssetSection eyebrow={ASSET_COPY.price.eyebrow} wrap={ASSET_COPY.price.wrap}>
          <PriceRegimeChart
            symbol={sym}
            initialBars={detail.bars?.bars ?? []}
            regime={detail.state?.regime}
            stale={detail.bars?.provenance.stale}
          />
        </AssetSection>

        <AssetSection eyebrow={ASSET_COPY.fit.eyebrow} wrap={ASSET_COPY.fit.wrap}>
          <FitField symbol={sym} initial={fitSeed} />
        </AssetSection>

        <AssetSection
          eyebrow={ASSET_COPY.character.eyebrow}
          wrap={ASSET_COPY.character.wrap}
        >
          <div className="grid gap-6 lg:grid-cols-2">
            <ProfileDossier profile={detail.profile} />
            <CorrelationField profile={detail.profile} />
          </div>
        </AssetSection>

        <AssetSection eyebrow={ASSET_COPY.state.eyebrow} wrap={ASSET_COPY.state.wrap}>
          <div className="grid gap-6 lg:grid-cols-2">
            <RegimeNowcastField state={detail.state} />
            <RegimeHistoryField profile={detail.profile} />
          </div>
        </AssetSection>

        <AssetSection eyebrow={ASSET_COPY.events.eyebrow} wrap={ASSET_COPY.events.wrap}>
          <EventSensitivityField profile={detail.profile} />
        </AssetSection>

        <AssetSection
          eyebrow={ASSET_COPY.narrative.eyebrow}
          wrap={ASSET_COPY.narrative.wrap}
        >
          <div className="grid gap-6 lg:grid-cols-2">
            <SentimentField sentiment={detail.sentiment} />
            <DriverPress sentiment={detail.sentiment} />
          </div>
        </AssetSection>

        <AssetSection eyebrow={ASSET_COPY.insight.eyebrow} wrap={ASSET_COPY.insight.wrap}>
          <InsightBrief insight={detail.insight} />
        </AssetSection>
      </div>
    </AppShell>
  );
}
