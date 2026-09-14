"use server";

import { fetchApi } from "@/lib/api/client";
import type { ApiKeyListResponse, MintKeyResponse } from "@/lib/api/types";

function key(): string {
  const k = process.env.OUROBOROS_SERVER_API_KEY;
  if (!k) throw new Error("OUROBOROS_SERVER_API_KEY is not set");
  return k;
}

export async function listKeysAction(): Promise<ApiKeyListResponse> {
  return fetchApi<ApiKeyListResponse>("/v1/admin/keys", { serverApiKey: key() });
}

export async function mintKeyAction(input: {
  name: string;
  service_name: string;
  role: string;
}): Promise<MintKeyResponse> {
  return fetchApi<MintKeyResponse>("/v1/admin/keys", {
    method: "POST",
    serverApiKey: key(),
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
}

export async function revokeKeyAction(id: number): Promise<void> {
  await fetchApi(`/v1/admin/keys/${id}/revoke`, {
    method: "POST",
    serverApiKey: key(),
  });
}
