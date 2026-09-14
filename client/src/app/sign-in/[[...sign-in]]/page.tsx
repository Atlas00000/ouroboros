import { SignIn } from "@clerk/nextjs";

import { EmptyState } from "@/components/ui/PageState";

export default function SignInPage() {
  if (!process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY) {
    return (
      <main id="main" className="flex min-h-screen items-center justify-center p-8">
        <EmptyState title="Sign-in unavailable" className="max-w-md text-center">
          Set <code className="font-mono text-foreground">NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY</code>{" "}
          and <code className="font-mono text-foreground">CLERK_SECRET_KEY</code> in{" "}
          <code className="font-mono text-foreground">.env.local</code> (invite-only org). Without
          Clerk, local routes stay open for development.
        </EmptyState>
      </main>
    );
  }

  return (
    <main id="main" className="flex min-h-screen items-center justify-center p-8">
      <h1 className="sr-only">Sign in to Ouroboros</h1>
      <SignIn />
    </main>
  );
}
