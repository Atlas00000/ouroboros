# ADR-016: Resend for human-facing email

- **Status:** Accepted
- **Date:** 2026-09-11
- **Roadmap ref:** Decision #16

## Context

Watchdog and scoring alerts must reach people when nobody is on the dashboard. Telegram/webhook alone are optional and not always available to stakeholders.

## Options

1. Telegram/webhook only
2. SMTP self-managed
3. Resend as primary email channel; Telegram/webhook remain optional (`ALERT_CHANNEL=multi`)

## Decision

Option 3. Resend sends staleness/watchdog alerts, optional digests, and weekly scoring summaries. Domain authenticated with SPF/DKIM/DMARC. Clerk invite/lifecycle mail may also use Resend.

## Consequences

- New secret: `RESEND_API_KEY`, `EMAIL_FROM`, `EMAIL_ALERT_TO`
- Email path proven at W3·D4 with the watchdog
- If Resend is down, multi-channel fallback still notifies ops
