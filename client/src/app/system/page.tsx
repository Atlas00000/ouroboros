import { AppShell } from "@/components/AppShell";
import { RoleGate } from "@/components/auth/RoleGate";
import { PipeHealthStrip } from "@/components/system/PipeHealthStrip";
import { FeedRegistryTable } from "@/components/system/FeedRegistryTable";
import { WatchdogAlertsList } from "@/components/system/WatchdogAlertsList";
import {
  fetchOpsSummaryServer,
  fetchRegistryServer,
  fetchWatchdogServer,
} from "@/lib/queries/system";

export const dynamic = "force-dynamic";

export default async function SystemPage() {
  const [registry, watchdog, summary] = await Promise.all([
    fetchRegistryServer(),
    fetchWatchdogServer(),
    fetchOpsSummaryServer(),
  ]);

  return (
    <AppShell>
      <div>
        <h1 className="text-lg font-semibold tracking-tight">System</h1>
        <p className="mt-1 max-w-xl text-sm text-muted">
          Trust the pipe — feeds, watchdog, outbox depth. Ops/admin only.
        </p>
      </div>
      <RoleGate minRole="admin">
        <div className="flex flex-col gap-6">
          <PipeHealthStrip data={summary} />
          <FeedRegistryTable data={registry} />
          <WatchdogAlertsList data={watchdog} />
        </div>
      </RoleGate>
    </AppShell>
  );
}
