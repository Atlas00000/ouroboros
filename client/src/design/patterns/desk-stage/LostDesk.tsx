"use client";

import Link from "next/link";

import { DeskSignalField } from "@/design/patterns/desk-stage/DeskSignalField";
import { DeskStage } from "@/design/patterns/desk-stage/DeskStage";

/**
 * Full-bleed 404 — instrument field in halt tone, clear path back to the desk.
 */
export function LostDesk() {
  return (
    <DeskStage label="Page not found">
      <DeskSignalField pulse={0.72} tone="halt" />

      <p className="ds-desk-lost__code" aria-hidden>
        404
      </p>

      <header className="ds-desk-stage__mast">
        <p className="ds-desk-stage__eyebrow">Signal lost · off the board</p>
        <h1 className="ds-desk-stage__title" data-tone="halt">
          No desk
          <br />
          at this mark
        </h1>
        <p className="ds-desk-stage__lede">
          That route is not on the watchlist. The ledger is intact — return to
          the board, open the tape, or jump a known instrument dossier.
        </p>
      </header>

      <ul className="ds-desk-lost__hints">
        <li>Research only</li>
        <li>No execution</li>
        <li>Profiles for siblings</li>
      </ul>

      <div className="ds-desk-stage__actions">
        <Link href="/" className="ds-desk-stage__cta">
          Back to the board →
        </Link>
        <Link href="/news" className="ds-desk-stage__ghost">
          Open the tape
        </Link>
        <Link href="/system" className="ds-desk-stage__ghost">
          Desk ops
        </Link>
      </div>
    </DeskStage>
  );
}
