"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { UserButton } from "@clerk/nextjs";
import { useEffect, useState } from "react";

import { readE2eRoleCookie, useClerkAppRole } from "@/components/auth/RoleGate";
import { roleAtLeast, type AppRole } from "@/lib/auth/roles";
import { cn } from "@/lib/utils";

const clerkEnabled = Boolean(process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY);

type NavLink = { href: string; label: string; minRole?: AppRole };

const LINKS: NavLink[] = [
  { href: "/", label: "Dashboard" },
  { href: "/news", label: "News" },
  { href: "/scoring", label: "Scoring" },
  { href: "/system", label: "System", minRole: "admin" },
  { href: "/admin/keys", label: "Admin", minRole: "admin" },
];

function linkActive(pathname: string, href: string): boolean {
  return href === "/" ? pathname === "/" : pathname === href || pathname.startsWith(`${href}/`);
}

function NavLinks({ role }: { role: AppRole | null }) {
  const pathname = usePathname();
  const visible = LINKS.filter((l) => {
    if (!l.minRole) return true;
    if (role == null) return true;
    return roleAtLeast(role, l.minRole);
  });

  return (
    <nav className="flex items-center gap-3 overflow-x-auto" aria-label="Primary">
      {visible.map((l) => {
        const active = linkActive(pathname, l.href);
        return (
          <Link
            key={l.href}
            href={l.href}
            aria-current={active ? "page" : undefined}
            className={cn(
              "whitespace-nowrap text-xs hover:text-foreground focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent",
              active ? "text-foreground" : "text-muted",
            )}
          >
            {l.label}
          </Link>
        );
      })}
    </nav>
  );
}

function ClerkRoleLinks() {
  const { loaded, role } = useClerkAppRole();
  return <NavLinks role={loaded ? role : null} />;
}

function LocalOrE2eLinks() {
  const [role, setRole] = useState<AppRole | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    setRole(readE2eRoleCookie() ?? "ops");
    setReady(true);
  }, []);

  if (!ready) return <NavLinks role={null} />;
  return <NavLinks role={role} />;
}

export function AppNav() {
  return (
    <header className="border-b border-border bg-card/80 backdrop-blur">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between gap-4 px-4">
        <div className="flex min-w-0 items-center gap-6">
          <Link
            href="/"
            className="flex shrink-0 items-center gap-2 text-sm font-semibold tracking-tight text-foreground focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="/logo.svg" alt="" width={22} height={22} className="opacity-90" />
            <span>Ouroboros</span>
          </Link>
          {clerkEnabled ? <ClerkWithE2eOverride /> : <LocalOrE2eLinks />}
        </div>
        <div className="flex shrink-0 items-center gap-3">
          {clerkEnabled ? (
            <UserButton />
          ) : (
            <span className="text-[11px] text-muted">Clerk keys unset</span>
          )}
        </div>
      </div>
    </header>
  );
}

function ClerkWithE2eOverride() {
  const [e2e, setE2e] = useState<AppRole | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    setE2e(readE2eRoleCookie());
    setReady(true);
  }, []);

  if (!ready) return <NavLinks role={null} />;
  if (e2e != null) return <NavLinks role={e2e} />;
  return <ClerkRoleLinks />;
}
