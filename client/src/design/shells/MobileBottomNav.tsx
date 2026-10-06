"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  Home,
  LayoutDashboard,
  Newspaper,
  type LucideIcon,
} from "lucide-react";

import { Icon } from "@/design/primitives/Icon";
import {
  APP_NAV_LINKS,
  linkActive,
  type AppNavHref,
} from "@/design/shells/nav-config";

const DOCK_ICONS: Record<AppNavHref, LucideIcon> = {
  "/": Home,
  "/news": Newspaper,
  "/scoring": BarChart3,
  "/system": LayoutDashboard,
};

/** Fixed bottom dock — primary navigation on small viewports. */
export function MobileBottomNav() {
  const pathname = usePathname();

  return (
    <div className="ds-mobile-dock">
      <nav className="ds-mobile-dock__nav" aria-label="Primary mobile">
        {APP_NAV_LINKS.map((link) => {
          const active = linkActive(pathname, link.href);
          const glyph = DOCK_ICONS[link.href];
          return (
            <Link
              key={link.href}
              href={link.href}
              aria-current={active ? "page" : undefined}
              className="ds-mobile-dock__link"
            >
              <span className="ds-mobile-dock__icon">
                <Icon icon={glyph} size="md" />
              </span>
              <span>{link.short}</span>
            </Link>
          );
        })}
      </nav>
    </div>
  );
}
