import { ScoringResults } from "@/components/scoring/ScoringResults";
import { AppShell } from "@/design/shells/AppShell";
import { PageHeader } from "@/design/shells/PageHeader";
import { fetchWeeklyScoringServer } from "@/lib/queries/system";

export const dynamic = "force-dynamic";

export default async function ScoringPage() {
  const data = await fetchWeeklyScoringServer(12);

  return (
    <AppShell wide>
      <PageHeader
        title="Scoring"
        description="Weekly regime and fit-tag stickiness — honesty about the brain without claiming foresight."
      />
      <ScoringResults data={data} />
    </AppShell>
  );
}
