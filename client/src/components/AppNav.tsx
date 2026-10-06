"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { UserButton } from "@clerk/nextjs";

import { ThemeSwitcher } from "@/design/shells/ThemeSwitcher";
import { APP_NAV_LINKS, linkActive } from "@/design/shells/nav-config";
import { Text } from "@/design/primitives/Text";
import { cn } from "@/lib/utils";

const clerkEnabled = Boolean(process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY);

/** Desktop header — brand · centered nav · theme. Hidden below md. */
export function AppNav() {
  const pathname = usePathname();

  return (
    <header className="ds-desktop-nav sticky top-0 z-40 border-b border-ds-line bg-ds-canvas-elevated/85 shadow-[var(--ds-shadow-chrome)] backdrop-blur-md">
      <div className="mx-auto grid h-14 max-w-[var(--ds-shell-max)] grid-cols-[1fr_auto_1fr] items-center gap-3 px-4 sm:px-6 lg:px-8">
        <div className="flex min-w-0 items-center justify-self-start">
          <Link
            href="/"
            className="group flex shrink-0 items-center gap-2.5 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ds-signal"
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/logo.svg"
              alt=""
              width={22}
              height={22}
              className="opacity-90 transition-opacity duration-[var(--ds-duration-swift)] group-hover:opacity-100"
            />
            <Text
              as="span"
              variant="title"
              className="text-[length:var(--ds-text-body)] tracking-[var(--ds-text-title-tracking)]"
            >
              Ouroboros
            </Text>
            <span
              className="hidden h-1.5 w-1.5 rounded-full bg-ds-signal sm:inline-block"
              aria-hidden
            />
          </Link>
        </div>

        <nav
          className="flex items-center justify-center gap-1 overflow-x-auto sm:gap-2"
          aria-label="Primary"
        >
          {APP_NAV_LINKS.map((link) => {
            const active = linkActive(pathname, link.href);
            return (
              <Link
                key={link.href}
                href={link.href}
                aria-current={active ? "page" : undefined}
                className={cn(
                  "whitespace-nowrap rounded-[var(--ds-radius-md)] px-2.5 py-1.5 text-[length:var(--ds-text-label)] font-medium tracking-wide transition-colors duration-[var(--ds-duration-swift)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ds-signal",
                  active
                    ? "bg-ds-signal-soft text-ds-signal"
                    : "text-ds-ink-muted hover:bg-ds-plane-raised hover:text-ds-ink",
                )}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>

        <div className="flex shrink-0 items-center justify-end gap-2 justify-self-end sm:gap-3">
          <ThemeSwitcher />
          {clerkEnabled ? <UserButton /> : null}
        </div>
      </div>
    </header>
  );
}
