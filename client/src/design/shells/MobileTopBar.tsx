"use client";

import Link from "next/link";
import { UserButton } from "@clerk/nextjs";

import { ThemeSwitcher } from "@/design/shells/ThemeSwitcher";

const clerkEnabled = Boolean(process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY);

/** Compact mobile top strip — brand + theme (nav lives in the dock). */
export function MobileTopBar() {
  return (
    <header className="ds-mobile-top" aria-label="Mobile desk header">
      <div className="ds-mobile-top__inner">
        <Link href="/" className="ds-mobile-top__brand">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/logo.svg" alt="" width={20} height={20} />
          <span className="ds-mobile-top__wordmark">Ouroboros</span>
        </Link>
        <div className="ds-mobile-top__actions">
          <ThemeSwitcher />
          {clerkEnabled ? <UserButton /> : null}
        </div>
      </div>
    </header>
  );
}
