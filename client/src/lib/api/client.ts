/** Runtime API helpers — browser attaches Clerk JWT; RSC may use server key. */

const DEFAULT_API = "http://localhost:8000";

export function apiBaseUrl(): string {
  const raw = process.env.NEXT_PUBLIC_API_URL || DEFAULT_API;
  return raw.replace(/\/$/, "");
}

export class ApiError extends Error {
  status: number;
  body: unknown;

  constructor(status: number, body: unknown, message?: string) {
    super(message || `API ${status}`);
    this.status = status;
    this.body = body;
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
  const h = new Headers(headers);
  if (!h.has("Accept")) h.set("Accept", "application/json");
  if (token) h.set("Authorization", `Bearer ${token}`);
  else if (serverApiKey) h.set("X-API-Key", serverApiKey);

  const res = await fetch(url, { ...init, headers: h, cache: "no-store" });
  if (!res.ok) {
    let body: unknown = null;
    try {
      body = await res.json();
    } catch {
      body = await res.text();
    }
    throw new ApiError(res.status, body);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}
