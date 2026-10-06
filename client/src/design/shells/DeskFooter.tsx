import Link from "next/link";

import "./desk-footer.css";

const DESK_LINKS = [
  { href: "/", label: "Board" },
  { href: "/news", label: "Tape" },
  { href: "/scoring", label: "Scoring" },
  { href: "/system", label: "Ops" },
] as const;

const HONESTY = [
  { label: "Research", detail: "Context only" },
  { label: "No execution", detail: "Never a broker" },
  { label: "Profiles", detail: "For sibling stacks" },
] as const;

/**
 * Desk footer — brand + honesty contract, not a generic legal strip.
 */
export function DeskFooter() {
  return (
    <footer className="ds-desk-footer" aria-label="Desk colophon">
      <div className="ds-desk-footer__rule" aria-hidden />
      <div className="ds-desk-footer__inner">
        <div className="ds-desk-footer__brand">
          <p className="ds-desk-footer__eyebrow">Signal desk · research only</p>
          <div className="ds-desk-footer__wordmark">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="/logo.svg" alt="" width={18} height={18} />
            <span>Ouroboros</span>
          </div>
          <p className="ds-desk-footer__lede">
            Living asset profiles staged for sibling platforms. Price paths,
            regimes, and narrative pressure on one ledger — never trade
            routing, never advice.
          </p>
        </div>

        <div className="ds-desk-footer__meta">
          <nav className="ds-desk-footer__nav" aria-label="Desk shortcuts">
            {DESK_LINKS.map((link) => (
              <Link key={link.href} href={link.href} className="ds-desk-footer__nav-link">
                {link.label}
              </Link>
            ))}
          </nav>

          <ul className="ds-desk-footer__honesty">
            {HONESTY.map((item) => (
              <li key={item.label}>
                <span className="ds-desk-footer__honesty-label">{item.label}</span>
                <span className="ds-desk-footer__honesty-detail">{item.detail}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="ds-desk-footer__colophon">
        <span className="ds-desk-footer__mark" aria-hidden />
        <p>
          Internal research context. Outputs do not constitute investment advice
          and do not execute trades.
        </p>
      </div>
    </footer>
  );
}
