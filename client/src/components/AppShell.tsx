/** Shared page chrome — landmarks + research disclaimer. */

import type { ReactNode } from "react";

import { AppNav } from "@/components/AppNav";

export function AppShell({
  children,
  mainClassName = "mx-auto flex w-full max-w-6xl flex-1 flex-col gap-6 px-4 py-6",
}: {
  children: ReactNode;
  mainClassName?: string;
}) {
  return (
    <>
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded focus:bg-card focus:px-3 focus:py-2 focus:text-sm focus:text-foreground focus:outline focus:outline-2 focus:outline-accent"
      >
        Skip to content
      </a>
      <AppNav />
      <main id="main" className={mainClassName} tabIndex={-1}>
        {children}
      </main>
      <footer className="border-t border-border py-4">
        <p className="mx-auto max-w-6xl px-4 text-[11px] leading-snug text-muted">
          Ouroboros provides internal research context only. Outputs are not investment advice and do
          not execute trades.
        </p>
      </footer>
    </>
  );
}
