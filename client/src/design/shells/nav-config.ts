/** Shared primary nav — desk + mobile chrome. */

export const APP_NAV_LINKS = [
  { href: "/", label: "Home", short: "Home" },
  { href: "/news", label: "News", short: "News" },
  { href: "/scoring", label: "Scoring", short: "Score" },
  { href: "/system", label: "Desk", short: "Desk" },
] as const;

export type AppNavHref = (typeof APP_NAV_LINKS)[number]["href"];

export function linkActive(pathname: string, href: string): boolean {
  return href === "/"
    ? pathname === "/"
    : pathname === href || pathname.startsWith(`${href}/`);
}
