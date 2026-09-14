import { SignUp } from "@clerk/nextjs";

export default function SignUpPage() {
  if (!process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY) {
    return (
      <main className="flex min-h-screen items-center justify-center p-8">
        <p className="text-muted max-w-md text-center text-sm">
          Public sign-up is disabled in production (invite-only). Configure Clerk keys to enable
          the hosted invite/sign-up flow.
        </p>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen items-center justify-center p-8">
      <SignUp />
    </main>
  );
}
