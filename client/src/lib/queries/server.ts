import { fetchApi } from "@/lib/api/client";
import type { AssetListResponse, NewsListResponse } from "@/lib/api/types";

/** Server-side fetch for RSC — uses server-only API key when Clerk JWT unavailable. */
export async function fetchAssetsServer(): Promise<AssetListResponse | null> {
  const key = process.env.OUROBOROS_SERVER_API_KEY;
  if (!key) return null;
  try {
    return await fetchApi<AssetListResponse>("/v1/assets?limit=50&active_only=true", {
      serverApiKey: key,
    });
  } catch {
    return null;
  }
}

export async function fetchNewsServer(limit = 8): Promise<NewsListResponse | null> {
  const key = process.env.OUROBOROS_SERVER_API_KEY;
  if (!key) return null;
  try {
    return await fetchApi<NewsListResponse>(`/v1/news?limit=${limit}`, {
      serverApiKey: key,
    });
  } catch {
    return null;
  }
}
