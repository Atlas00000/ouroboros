"use client";

import { useEffect, useId, useRef } from "react";
import { createPortal } from "react-dom";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";

import { StateBadge } from "@/components/StateBadge";
import { StaleBadge } from "@/components/StaleBadge";
import {
  cssVarForTone,
  REGIME_LABEL,
  toneForRegime,
  type Regime,
} from "@/design/map/backend-visual";
import { Button } from "@/design/primitives/Button";
import { UniverseMiniChart } from "@/design/patterns/universe/UniverseMiniChart";
import { UniverseSentiment } from "@/design/patterns/universe/UniverseSentiment";
import { UniverseVolGauge } from "@/design/patterns/universe/UniverseVolGauge";
import {
  UNIVERSE_SPARK_LABEL,
  type UniverseChartType,
  type UniverseSparkSeries,
  type UniverseSparkTimeframe,
} from "@/design/patterns/universe/spark";
import type { DashboardCard } from "@/lib/queries/dashboard";

type UniverseFocusProps = {
  card: DashboardCard;
  timeframe: UniverseSparkTimeframe;
  chartType: UniverseChartType;
  onClose: () => void;
};

function formatClose(n: number | null | undefined): string {
  if (n == null || Number.isNaN(n)) return "—";
  if (Math.abs(n) >= 1000) return n.toFixed(1);
  if (Math.abs(n) >= 1) return n.toFixed(4);
  return n.toPrecision(5);
}

function formatChange(pct: number | null | undefined): string {
  if (pct == null || Number.isNaN(pct)) return "—";
  const sign = pct > 0 ? "+" : "";
  return `${sign}${pct.toFixed(2)}%`;
}

function changeTone(pct: number | null | undefined): "up" | "down" | "flat" {
  if (pct == null || Number.isNaN(pct) || pct === 0) return "flat";
  return pct > 0 ? "up" : "down";
}

/**
 * Desk focus — full-screen blur scrim + instrument mini-window.
 * Stay on Home; open the full dossier only when asked.
 */
export function UniverseFocus({
  card,
  timeframe,
  chartType,
  onClose,
}: UniverseFocusProps) {
  const { asset, regime, volPercentile, sentimentScore, stale } = card;
  const tone = cssVarForTone(toneForRegime(regime as Regime));
  const titleId = useId();
  const closeRef = useRef<HTMLButtonElement>(null);

  const seriesQ = useQuery({
    queryKey: ["universe-spark", timeframe, asset.symbol],
    staleTime: 60_000,
    queryFn: async (): Promise<UniverseSparkSeries> => {
      const params = new URLSearchParams({
        symbol: asset.symbol,
        timeframe,
      });
      const res = await fetch(`/api/universe-spark?${params}`, { cache: "no-store" });
      if (!res.ok) throw new Error(`spark ${res.status}`);
      return (await res.json()) as UniverseSparkSeries;
    },
  });

  const lastClose = seriesQ.data?.lastClose ?? null;
  const changePct = seriesQ.data?.changePct ?? null;
  const regimeLabel = regime ? (REGIME_LABEL[regime] ?? regime) : "—";

  useEffect(() => {
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    const previouslyFocused = document.activeElement as HTMLElement | null;
    closeRef.current?.focus();

    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        onClose();
      }
    };
    window.addEventListener("keydown", onKey);

    return () => {
      document.body.style.overflow = prevOverflow;
      window.removeEventListener("keydown", onKey);
      previouslyFocused?.focus?.();
    };
  }, [onClose]);

  const pair =
    asset.base_currency && asset.quote_currency
      ? `${asset.base_currency} / ${asset.quote_currency}`
      : null;

  const node = (
    <div
      className="ds-universe-focus"
      role="presentation"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        className="ds-universe-focus__panel"
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        style={{ ["--ds-instrument-tone" as string]: tone }}
        tabIndex={-1}
      >
        <header className="ds-universe-focus__head">
          <div className="ds-universe-focus__id">
            <p className="ds-universe-focus__eyebrow">Instrument focus</p>
            <div className="ds-universe-focus__title-row">
              <h2 id={titleId} className="ds-universe-focus__symbol">
                {asset.symbol}
              </h2>
              <StateBadge regime={regime} />
              <StaleBadge stale={stale} />
            </div>
            <p className="ds-universe-focus__name">{asset.display_name}</p>
          </div>
          <button
            ref={closeRef}
            type="button"
            className="ds-universe-focus__close"
            onClick={onClose}
            aria-label="Close instrument focus"
          >
            Close
          </button>
        </header>

        <p className="ds-universe-focus__lede">
          Desk cut for {asset.symbol} — regime {regimeLabel.toLowerCase()},{" "}
          {UNIVERSE_SPARK_LABEL[timeframe]} path on the board. Research context
          only; open the full dossier when you need the living profile.
        </p>

        <div className="ds-universe-focus__chart">
          <UniverseMiniChart
            symbol={asset.symbol}
            closes={seriesQ.data?.closes}
            bars={seriesQ.data?.bars}
            chartType={chartType}
            regime={regime}
            loading={seriesQ.isLoading}
            timeframeLabel={UNIVERSE_SPARK_LABEL[timeframe]}
          />
        </div>

        <dl className="ds-universe-focus__metrics">
          <div>
            <dt>Last</dt>
            <dd className="ds-universe-focus__px">{formatClose(lastClose)}</dd>
          </div>
          <div>
            <dt>Window</dt>
            <dd data-tone={changeTone(changePct)}>{formatChange(changePct)}</dd>
          </div>
          <div>
            <dt>Regime</dt>
            <dd>{regimeLabel}</dd>
          </div>
          <div>
            <dt>Class</dt>
            <dd className="ds-universe-focus__caps">{asset.asset_class}</dd>
          </div>
          {pair ? (
            <div>
              <dt>Pair</dt>
              <dd>{pair}</dd>
            </div>
          ) : null}
          {asset.mt5_ticker ? (
            <div>
              <dt>Ticker</dt>
              <dd>{asset.mt5_ticker}</dd>
            </div>
          ) : null}
        </dl>

        <div className="ds-universe-focus__gauges">
          <UniverseVolGauge value={volPercentile} />
          <div className="ds-universe-focus__sent-block">
            <span className="ds-universe-focus__sent-label">Sentiment</span>
            <UniverseSentiment score={sentimentScore} />
          </div>
        </div>

        <footer className="ds-universe-focus__actions">
          <Button variant="ghost" size="md" onClick={onClose}>
            Stay on desk
          </Button>
          <Link href={`/assets/${asset.symbol}`} className="ds-universe-focus__dossier">
            Open full dossier →
          </Link>
        </footer>
      </div>
    </div>
  );

  if (typeof document === "undefined") return null;
  return createPortal(node, document.body);
}
