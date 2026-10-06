import type { ReactNode } from "react";

import { AppNav } from "@/components/AppNav";
import { PageEnter } from "@/design/motion/PageEnter";
import { DeskFooter } from "@/design/shells/DeskFooter";
import { MobileBottomNav } from "@/design/shells/MobileBottomNav";
import { MobileTopBar } from "@/design/shells/MobileTopBar";
import { cn } from "@/lib/utils";

import "./mobile-chrome.css";

type AppShellProps = {
  children?: ReactNode;
  /** Optional right rail (context / actions). */
  rail?: ReactNode;
  mainClassName?: string;
  /** Expand chrome + content to ~95vw (Home desk scan). */
  wide?: boolean;
};

/**
 * Global chrome: desktop header + mobile top/dock, ambient canvas, optional rail.
 * Section layouts compose inside `children` — do not restyle product sections here.
 */
export function AppShell({ children, rail, mainClassName, wide = false }: AppShellProps) {
  const hasBody = children != null || rail != null;

  return (
    <div
      className="ds-app relative flex min-h-full flex-1 flex-col"
      data-shell={wide ? "wide" : undefined}
      data-layout="responsive"
    >
      <div className="ds-app-ambient pointer-events-none absolute inset-0 -z-10" aria-hidden />
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-[var(--ds-radius-md)] focus:bg-ds-plane focus:px-3 focus:py-2 focus:text-sm focus:text-ds-ink focus:outline focus:outline-2 focus:outline-ds-signal"
      >
        Skip to content
      </a>
      <AppNav />
      <MobileTopBar />
      <main
        id="main"
        tabIndex={-1}
        className={cn(
          "ds-app-main mx-auto flex w-full max-w-[var(--ds-shell-max)] flex-1 flex-col gap-6 px-4 py-6 sm:px-6 lg:px-8",
          mainClassName,
        )}
      >
        {hasBody ? (
          <PageEnter>
            {rail ? (
              <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:gap-0">
                <div className="min-w-0 flex-1 space-y-6 lg:pr-6">{children}</div>
                <div className="ds-page-enter-delay">{rail}</div>
              </div>
            ) : (
              children
            )}
          </PageEnter>
        ) : null}
      </main>
      <DeskFooter />
      <MobileBottomNav />
    </div>
  );
}
