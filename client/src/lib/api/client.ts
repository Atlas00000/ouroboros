/** Runtime API helpers — browser attaches Clerk JWT; RSC may use server key. */

import {
  CLIENT_REQUEST_ID_HEADER,
  logApiCall,
  newClientRequestId,
} from "@/lib/log/api-log";

const DEFAULT_API = "http://localhost:8000";

export function apiBaseUrl(): string {
  // Server-side Docker/internal override; browser always uses NEXT_PUBLIC_*.
  const raw =
    (typeof window === "undefined" ? process.env.API_URL : undefined) ||
    process.env.NEXT_PUBLIC_API_URL ||
    DEFAULT_API;
  return raw.replace(/\/$/, "");
}

export class ApiError extends Error {
  status: number;
  body: unknown;
  requestId?: string;

  constructor(status: number, body: unknown, message?: string, requestId?: string) {
    super(message || `API ${status}`);
    this.status = status;
    this.body = body;
    this.requestId = requestId;
  }
}

export type FetchApiOptions = RequestInit & {
  token?: string | null;
  /** Server-only local hug — never expose as NEXT_PUBLIC_* */
  serverApiKey?: string | null;
};

export async function fetchApi<T>(
  path: string,
  options: FetchApiOptions = {},
): Promise<T> {
  const { token, serverApiKey, headers, ...init } = options;
  const url = `${apiBaseUrl()}${path.startsWith("/") ? path : `/${path}`}`;
  const method = (init.method || "GET").toUpperCase();
  const requestId = newClientRequestId();
  const h = new Headers(headers);
  if (!h.has("Accept")) h.set("Accept", "application/json");
  if (!h.has(CLIENT_REQUEST_ID_HEADER)) h.set(CLIENT_REQUEST_ID_HEADER, requestId);
  if (token) h.set("Authorization", `Bearer ${token}`);
  else if (serverApiKey) h.set("X-API-Key", serverApiKey);

  const started = performance.now();
  try {
    const res = await fetch(url, { ...init, headers: h, cache: "no-store" });
    const durationMs = performance.now() - started;
    const serverRid = res.headers.get(CLIENT_REQUEST_ID_HEADER) || requestId;

    if (!res.ok) {
      const raw = await res.text();
      let body: unknown = raw;
      if (raw) {
        try {
          body = JSON.parse(raw);
        } catch {
          /* keep text */
        }
      } else {
        body = null;
      }
      logApiCall({
        method,
        path,
        status: res.status,
        durationMs,
        requestId: serverRid,
        ok: false,
        error: `HTTP ${res.status}`,
      });
      throw new ApiError(res.status, body, undefined, serverRid);
    }

    logApiCall({
      method,
      path,
      status: res.status,
      durationMs,
      requestId: serverRid,
      ok: true,
    });

    if (res.status === 204) return undefined as T;
    return (await res.json()) as T;
  } catch (err) {
    if (err instanceof ApiError) throw err;
    const durationMs = performance.now() - started;
    logApiCall({
      method,
      path,
      durationMs,
      requestId,
      ok: false,
      error: err instanceof Error ? err.message : "fetch_failed",
    });
    throw err;
  }
}
