import { AppShell } from "@/components/AppShell";
import { ScoringResults } from "@/components/scoring/ScoringResults";
import { fetchWeeklyScoringServer } from "@/lib/queries/system";

export const dynamic = "force-dynamic";

export default async function ScoringPage() {
  const data = await fetchWeeklyScoringServer(12);

  return (
    <AppShell>
      <div>
        <h1 className="text-lg font-semibold tracking-tight">Scoring</h1>
        <p className="mt-1 max-w-xl text-sm text-muted">
          Weekly regime hit-rates — same story as the Resend digest. Builds trust without claiming
          foresight.
        </p>
      </div>
      <ScoringResults data={data} />
    </AppShell>
  );
}
