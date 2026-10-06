/**
 * API call timing / status logger — used by fetchApi wrapper.
 * Propagates X-Request-Id when present for correlation with server logs.
 */

import { createLogger } from "@/lib/log/logger";

const log = createLogger("api");

export const CLIENT_REQUEST_ID_HEADER = "X-Request-Id";

export function newClientRequestId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `c-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
}

export type ApiCallLogInput = {
  method: string;
  path: string;
  status?: number;
  durationMs: number;
  requestId: string;
  ok: boolean;
  error?: string;
};

export function logApiCall(input: ApiCallLogInput): void {
  const fields = {
    method: input.method,
    path: input.path,
    status: input.status,
    duration_ms: Math.round(input.durationMs),
    request_id: input.requestId,
  };
  if (!input.ok) {
    log.warn("api_call_failed", { ...fields, error: input.error });
    return;
  }
  if ((input.status ?? 0) >= 400) {
    log.warn("api_call", fields);
    return;
  }
  log.info("api_call", fields);
}
