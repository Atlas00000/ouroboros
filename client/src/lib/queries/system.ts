import { fetchApi } from "@/lib/api/client";
import type {
  OpsSummaryResponse,
  RegistryResponse,
  WatchdogResponse,
  WeeklyScoringResponse,
} from "@/lib/api/types";

function serverKey(): string | null {
  return process.env.OUROBOROS_SERVER_API_KEY || null;
}

export async function fetchRegistryServer(): Promise<RegistryResponse | null> {
  const key = serverKey();
  if (!key) return null;
  try {
    return await fetchApi<RegistryResponse>("/v1/ops/registry", { serverApiKey: key });
  } catch {
    return null;
  }
}

export async function fetchWatchdogServer(): Promise<WatchdogResponse | null> {
  const key = serverKey();
  if (!key) return null;
  try {
    return await fetchApi<WatchdogResponse>("/v1/ops/watchdog", { serverApiKey: key });
  } catch {
    return null;
  }
}

export async function fetchOpsSummaryServer(): Promise<OpsSummaryResponse | null> {
  const key = serverKey();
  if (!key) return null;
  try {
    return await fetchApi<OpsSummaryResponse>("/v1/ops/summary", { serverApiKey: key });
  } catch {
    return null;
  }
}

export async function fetchWeeklyScoringServer(
  limit = 8,
): Promise<WeeklyScoringResponse | null> {
  const key = serverKey();
  if (!key) return null;
  try {
    return await fetchApi<WeeklyScoringResponse>(`/v1/scoring/weekly?limit=${limit}`, {
      serverApiKey: key,
    });
  } catch {
    return null;
  }
}
