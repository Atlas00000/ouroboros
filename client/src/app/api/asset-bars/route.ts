import { NextRequest, NextResponse } from "next/server";

import {
  ASSET_BAR_DEFAULT,
  ASSET_BAR_LOOKBACK_DAYS,
  isAssetBarTimeframe,
  type AssetBarTimeframe,
} from "@/design/patterns/price-regime/timeframes";
import { ApiError, fetchApi } from "@/lib/api/client";
import type { BarsResponse } from "@/lib/queries/asset-detail";

/**
 * Server-side OHLCV for Asset dossier charts.
 * Query: symbol, timeframe (M15|H1|H4|D1, default H1).
 */
export async function GET(req: NextRequest) {
  const symbol = (req.nextUrl.searchParams.get("symbol") ?? "").trim().toUpperCase();
  if (!symbol || symbol.length > 24) {
    return NextResponse.json({ error: "symbol required" }, { status: 400 });
  }

  const rawTf = (req.nextUrl.searchParams.get("timeframe") ?? ASSET_BAR_DEFAULT).toUpperCase();
  const timeframe: AssetBarTimeframe = isAssetBarTimeframe(rawTf)
    ? rawTf
    : ASSET_BAR_DEFAULT;
  const lookback = ASSET_BAR_LOOKBACK_DAYS[timeframe];

  const key = process.env.OUROBOROS_SERVER_API_KEY;
  if (!key) {
    return NextResponse.json(
      { error: "OUROBOROS_SERVER_API_KEY not configured" },
      { status: 503 },
    );
  }

  try {
    const bars = await fetchApi<BarsResponse>(
      `/v1/bars?symbol=${encodeURIComponent(symbol)}&timeframe=${timeframe}&lookback_days=${lookback}`,
      { serverApiKey: key },
    );
    return NextResponse.json(bars);
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) {
      return NextResponse.json({
        symbol,
        timeframe,
        bars: [],
        provenance: {
          sources: [],
          generated_at: new Date().toISOString(),
          model_version: "asset-bars.empty",
          confidence: 0,
          stale: true,
        },
      } satisfies BarsResponse);
    }
    const status = err instanceof ApiError ? err.status : 502;
    return NextResponse.json({ error: "bars unavailable" }, { status });
  }
}
