import { RoleGate } from "@/components/auth/RoleGate";
import { FeedRegistryTable } from "@/components/system/FeedRegistryTable";
import { PipeHealthStrip } from "@/components/system/PipeHealthStrip";
import { WatchdogAlertsList } from "@/components/system/WatchdogAlertsList";
import { AppShell } from "@/design/shells/AppShell";
import { PageHeader } from "@/design/shells/PageHeader";
import {
  fetchOpsSummaryServer,
  fetchRegistryServer,
  fetchWatchdogServer,
} from "@/lib/queries/system";

export const dynamic = "force-dynamic";

export default async function DeskPage() {
  const [registry, watchdog, summary] = await Promise.all([
    fetchRegistryServer(),
    fetchWatchdogServer(),
    fetchOpsSummaryServer(),
  ]);

  return (
    <AppShell wide>
      <PageHeader
        title="Desk"
        description="Trust the research desk — feeds, watchdog alerts, and pipe health. Ops and above."
      />
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
