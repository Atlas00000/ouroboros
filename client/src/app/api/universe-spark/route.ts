import { NextRequest, NextResponse } from "next/server";

import {
  UNIVERSE_SPARK_DEFAULT,
  UNIVERSE_SPARK_LOOKBACK_DAYS,
  isUniverseSparkTimeframe,
  type UniverseSparkTimeframe,
} from "@/design/patterns/universe/spark";
import { ApiError, fetchApi } from "@/lib/api/client";
import { seriesFromBars } from "@/lib/queries/dashboard";

type BarsPayload = {
  bars?: { open?: number; high?: number; low?: number; close: number }[];
};

/**
 * Server-side spark for Universe tiles.
 * Query: symbol (required), timeframe (M1|M15|H1|H4|D1, default M15).
 */
export async function GET(req: NextRequest) {
  const symbol = (req.nextUrl.searchParams.get("symbol") ?? "").trim().toUpperCase();
  if (!symbol || symbol.length > 24) {
    return NextResponse.json({ error: "symbol required" }, { status: 400 });
  }

  const rawTf = (req.nextUrl.searchParams.get("timeframe") ?? UNIVERSE_SPARK_DEFAULT).toUpperCase();
  const timeframe: UniverseSparkTimeframe = isUniverseSparkTimeframe(rawTf)
    ? rawTf
    : UNIVERSE_SPARK_DEFAULT;
  const lookback = UNIVERSE_SPARK_LOOKBACK_DAYS[timeframe];

  const key = process.env.OUROBOROS_SERVER_API_KEY;
  if (!key) {
    return NextResponse.json(
      { error: "OUROBOROS_SERVER_API_KEY not configured" },
      { status: 503 },
    );
  }

  try {
    const bars = await fetchApi<BarsPayload>(
      `/v1/bars?symbol=${encodeURIComponent(symbol)}&timeframe=${timeframe}&lookback_days=${lookback}`,
      { serverApiKey: key },
    );
    const series = seriesFromBars(bars.bars);
    return NextResponse.json({
      symbol,
      timeframe,
      ...series,
    });
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) {
      return NextResponse.json({
        symbol,
        timeframe,
        closes: [],
        bars: [],
        lastClose: null,
        changePct: null,
      });
    }
    const status = err instanceof ApiError ? err.status : 502;
    return NextResponse.json({ error: "bars unavailable" }, { status });
  }
}
