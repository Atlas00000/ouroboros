"use client";

import { useAuth } from "@clerk/nextjs";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useCallback, useEffect, useState, useTransition } from "react";

import { ApiError, fetchApi } from "@/lib/api/client";
import {
  listKeysAction,
  mintKeyAction,
  revokeKeyAction,
} from "@/lib/actions/admin-keys";
import type { ApiKeyListResponse, ApiKeyPublic, MintKeyResponse } from "@/lib/api/types";

const clerkEnabled = Boolean(process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY);

function formatErr(err: unknown): string {
  if (err instanceof ApiError) {
    const body = err.body as { detail?: string } | null;
    return body?.detail || err.message;
  }
  return err instanceof Error ? err.message : "Request failed";
}

function AdminKeysView({
  items,
  loading,
  error,
  revealed,
  onDismissReveal,
  name,
  service,
  role,
  onName,
  onService,
  onRole,
  minting,
  mintError,
  onMint,
  onRevoke,
  revoking,
}: {
  items?: ApiKeyPublic[];
  loading: boolean;
  error: string | null;
  revealed: string | null;
  onDismissReveal: () => void;
  name: string;
  service: string;
  role: string;
  onName: (v: string) => void;
  onService: (v: string) => void;
  onRole: (v: string) => void;
  minting: boolean;
  mintError: string | null;
  onMint: () => void;
  onRevoke: (id: number) => void;
  revoking: boolean;
}) {
  return (
    <div className="space-y-4">
      {revealed ? (
        <div className="rounded-md border border-regime-high-vol/40 bg-card p-3" role="status">
          <p className="text-sm font-medium text-foreground">Copy this key now</p>
          <p className="mt-1 text-[11px] text-muted">Plaintext is shown once and never stored.</p>
          <code className="mt-2 block break-all rounded bg-background px-2 py-2 font-mono text-xs">
            {revealed}
          </code>
          <button
            type="button"
            className="mt-2 text-xs text-accent underline"
            onClick={onDismissReveal}
          >
            Dismiss
          </button>
        </div>
      ) : null}

      <section className="rounded-md border border-border bg-card p-3">
        <h2 className="text-sm font-medium">Mint key</h2>
        <form
          className="mt-3 flex flex-col gap-2 sm:flex-row sm:flex-wrap sm:items-end"
          onSubmit={(e) => {
            e.preventDefault();
            onMint();
          }}
        >
          <label className="flex flex-col gap-1 text-[11px] text-muted">
            Name
            <input
              className="rounded border border-border bg-background px-2 py-1.5 font-mono text-xs text-foreground"
              value={name}
              onChange={(e) => onName(e.target.value)}
              pattern="[a-zA-Z0-9_\-]+"
              required
              minLength={2}
            />
          </label>
          <label className="flex flex-col gap-1 text-[11px] text-muted">
            Service
            <input
              className="rounded border border-border bg-background px-2 py-1.5 text-xs text-foreground"
              value={service}
              onChange={(e) => onService(e.target.value)}
              required
              minLength={2}
            />
          </label>
          <label className="flex flex-col gap-1 text-[11px] text-muted">
            Role
            <select
              className="rounded border border-border bg-background px-2 py-1.5 text-xs text-foreground"
              value={role}
              onChange={(e) => onRole(e.target.value)}
            >
              <option value="viewer">viewer</option>
              <option value="analyst">analyst</option>
              <option value="admin">admin</option>
              <option value="ops">ops</option>
            </select>
          </label>
          <button
            type="submit"
            disabled={minting || !name}
            className="rounded bg-accent px-3 py-1.5 text-xs font-medium text-background disabled:opacity-40"
          >
            {minting ? "Minting…" : "Mint"}
          </button>
        </form>
        {mintError ? <p className="mt-2 text-xs text-regime-trending-down">{mintError}</p> : null}
      </section>

      <section className="rounded-md border border-border bg-card p-3">
        <h2 className="text-sm font-medium">Keys</h2>
        {loading ? <p className="mt-2 text-sm text-muted">Loading…</p> : null}
        {error ? <p className="mt-2 text-sm text-regime-trending-down">{error}</p> : null}
        {items && !items.length ? (
          <p className="mt-2 text-sm text-muted">No keys yet.</p>
        ) : null}
        {items && items.length ? (
          <ul className="mt-3 divide-y divide-border">
            {items.map((k) => (
              <li
                key={k.id}
                className="flex flex-wrap items-center justify-between gap-2 py-2 text-xs"
              >
                <div>
                  <span className="font-mono text-foreground">{k.name}</span>
                  <span className="ml-2 text-muted">
                    {k.service_name} · {k.role} · {k.is_active ? "active" : "revoked"}
                  </span>
                </div>
                {k.is_active ? (
                  <button
                    type="button"
                    disabled={revoking}
                    className="text-regime-trending-down underline disabled:opacity-40"
                    onClick={() => onRevoke(k.id)}
                  >
                    Revoke
                  </button>
                ) : null}
              </li>
            ))}
          </ul>
        ) : null}
      </section>
    </div>
  );
}

function KeysPanelClerk() {
  const { getToken } = useAuth();
  const qc = useQueryClient();
  const [name, setName] = useState("");
  const [service, setService] = useState("quant");
  const [role, setRole] = useState("viewer");
  const [revealed, setRevealed] = useState<string | null>(null);

  const list = useQuery({
    queryKey: ["admin", "keys"],
    queryFn: async () => {
      const token = await getToken();
      return fetchApi<ApiKeyListResponse>("/v1/admin/keys", { token });
    },
  });

  const mint = useMutation({
    mutationFn: async () => {
      const token = await getToken();
      return fetchApi<MintKeyResponse>("/v1/admin/keys", {
        method: "POST",
        token,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, service_name: service, role }),
      });
    },
    onSuccess: (data) => {
      setRevealed(data.plaintext);
      setName("");
      void qc.invalidateQueries({ queryKey: ["admin", "keys"] });
    },
  });

  const revoke = useMutation({
    mutationFn: async (id: number) => {
      const token = await getToken();
      return fetchApi(`/v1/admin/keys/${id}/revoke`, { method: "POST", token });
    },
    onSuccess: () => void qc.invalidateQueries({ queryKey: ["admin", "keys"] }),
  });

  return (
    <AdminKeysView
      items={list.data?.items}
      loading={list.isLoading}
      error={list.error ? formatErr(list.error) : null}
      revealed={revealed}
      onDismissReveal={() => setRevealed(null)}
      name={name}
      service={service}
      role={role}
      onName={setName}
      onService={setService}
      onRole={setRole}
      minting={mint.isPending}
      mintError={mint.error ? formatErr(mint.error) : null}
      onMint={() => mint.mutate()}
      onRevoke={(id) => revoke.mutate(id)}
      revoking={revoke.isPending}
    />
  );
}

function KeysPanelLocal() {
  const [name, setName] = useState("");
  const [service, setService] = useState("quant");
  const [role, setRole] = useState("viewer");
  const [revealed, setRevealed] = useState<string | null>(null);
  const [items, setItems] = useState<ApiKeyPublic[] | undefined>();
  const [error, setError] = useState<string | null>(null);
  const [mintError, setMintError] = useState<string | null>(null);
  const [pending, startTransition] = useTransition();

  const refresh = useCallback(() => {
    startTransition(async () => {
      try {
        const data = await listKeysAction();
        setItems(data.items);
        setError(null);
      } catch (e) {
        setError(formatErr(e));
      }
    });
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return (
    <AdminKeysView
      items={items}
      loading={pending && items === undefined}
      error={error}
      revealed={revealed}
      onDismissReveal={() => setRevealed(null)}
      name={name}
      service={service}
      role={role}
      onName={setName}
      onService={setService}
      onRole={setRole}
      minting={pending}
      mintError={mintError}
      onMint={() => {
        startTransition(async () => {
          try {
            const data = await mintKeyAction({
              name,
              service_name: service,
              role,
            });
            setRevealed(data.plaintext);
            setName("");
            setMintError(null);
            const listed = await listKeysAction();
            setItems(listed.items);
          } catch (e) {
            setMintError(formatErr(e));
          }
        });
      }}
      onRevoke={(id) => {
        startTransition(async () => {
          try {
            await revokeKeyAction(id);
            setMintError(null);
            const listed = await listKeysAction();
            setItems(listed.items);
          } catch (e) {
            setMintError(formatErr(e));
          }
        });
      }}
      revoking={pending}
    />
  );
}

export function AdminKeysPanel() {
  if (!clerkEnabled) return <KeysPanelLocal />;
  return <KeysPanelClerk />;
}
