"use client";

import { useUser } from "@clerk/nextjs";
import { useEffect, useState, type ReactNode } from "react";

import { ErrorState, LoadingState } from "@/components/ui/PageState";
import {
  type AppRole,
  parseRole,
  roleAtLeast,
  roleFromMetadata,
} from "@/lib/auth/roles";

const clerkEnabled = Boolean(process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY);

/** Playwright sets `e2e_role=viewer` to exercise RoleGate without Clerk. */
export function readE2eRoleCookie(): AppRole | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie.match(/(?:^|; )e2e_role=([^;]*)/);
  if (!match?.[1]) return null;
  return parseRole(decodeURIComponent(match[1]));
}

type Props = {
  minRole: AppRole;
  children: ReactNode;
  fallback?: ReactNode;
};

function Denied({ minRole, role }: { minRole: AppRole; role: AppRole }) {
  return (
    <ErrorState title="Access denied">
      <p>
        This surface requires role <code className="font-mono text-foreground">{minRole}</code> or
        higher. Your role is <code className="font-mono text-foreground">{role}</code>.
      </p>
    </ErrorState>
  );
}

export function RoleGate({ minRole, children, fallback }: Props) {
  const [e2eRole, setE2eRole] = useState<AppRole | null>(null);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    setE2eRole(readE2eRoleCookie());
    setHydrated(true);
  }, []);

  if (!hydrated) {
    return <LoadingState>Checking access…</LoadingState>;
  }

  if (e2eRole != null) {
    if (!roleAtLeast(e2eRole, minRole)) {
      return fallback ?? <Denied minRole={minRole} role={e2eRole} />;
    }
    return <>{children}</>;
  }

  if (!clerkEnabled) {
    return <>{children}</>;
  }

  return (
    <RoleGateClerk minRole={minRole} fallback={fallback}>
      {children}
    </RoleGateClerk>
  );
}

function RoleGateClerk({
  minRole,
  children,
  fallback,
}: {
  minRole: AppRole;
  children: ReactNode;
  fallback?: ReactNode;
}) {
  const { isLoaded, user } = useUser();

  if (!isLoaded) {
    return <LoadingState>Checking access…</LoadingState>;
  }

  const role = roleFromMetadata(
    user?.publicMetadata as Record<string, unknown> | undefined,
  );

  if (!roleAtLeast(role, minRole)) {
    return fallback ?? <Denied minRole={minRole} role={role} />;
  }

  return <>{children}</>;
}

/** For Clerk-enabled trees only (must be under ClerkProvider). */
export function useClerkAppRole(): { loaded: boolean; role: AppRole } {
  const { isLoaded, user } = useUser();
  if (!isLoaded) return { loaded: false, role: "viewer" };
  return {
    loaded: true,
    role: roleFromMetadata(user?.publicMetadata as Record<string, unknown> | undefined),
  };
}
