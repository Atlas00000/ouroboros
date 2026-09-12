# W3·D4 status — notifications

## Done

- Shared `Notifier` / `AlertMessage` interface under `server/app/notifications/`
- Channels: Resend (required path), Telegram, webhook, log, multi fan-out
- Watchdog `--notify` + `ops/notifications/send_test.py`
- Unit tests with `httpx.MockTransport` (no network)

## Prove email path

```powershell
cd server
py -3.12 ..\ops\notifications\send_test.py
py -3.12 ..\ops\watchdog\run.py check --notify
```

Live smoke on 2026-09-12 hit **Resend HTTP 403** — code path + auth header are wired; fix in Resend dashboard (verify sending domain / use a permitted `EMAIL_FROM`). Unit tests cover a successful send via `MockTransport`.
