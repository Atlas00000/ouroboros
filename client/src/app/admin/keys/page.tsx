import { AdminKeysPanel } from "@/components/admin/AdminKeysPanel";
import { AppShell } from "@/components/AppShell";
import { RoleGate } from "@/components/auth/RoleGate";

export const dynamic = "force-dynamic";

export default function AdminKeysPage() {
  return (
    <AppShell>
      <div>
        <h1 className="text-lg font-semibold tracking-tight">Admin · API keys</h1>
        <p className="mt-1 max-w-xl text-sm text-muted">
          Mint and revoke machine keys for quant platforms. Plaintext is shown once. Browser
          dashboard data calls use Clerk JWT — never embed machine keys in normal chrome.
        </p>
      </div>
      <RoleGate minRole="admin">
        <AdminKeysPanel />
      </RoleGate>
    </AppShell>
  );
}
