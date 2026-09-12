# Notifications (W3·D4)

Shared interface: `app.notifications.Notifier` / `AlertMessage`.

| Channel | Env | Notes |
| --- | --- | --- |
| `resend` (default) | `RESEND_API_KEY`, `EMAIL_FROM`, `EMAIL_ALERT_TO` | Required email path |
| `telegram` | `ALERT_TELEGRAM_BOT_TOKEN`, `ALERT_TELEGRAM_CHAT_ID` | Optional |
| `webhook` | `ALERT_WEBHOOK_URL` | Optional Slack-style JSON POST |
| `log` | — | Structured logs only |
| `multi` | any configured above | Fan-out; always includes log |

```powershell
cd server
# Smoke test (uses ALERT_CHANNEL from server/.env)
py -3.12 ..\ops\notifications\send_test.py

# Force log-only
py -3.12 ..\ops\notifications\send_test.py --channel log

# Watchdog check + email digest when stale feeds exist
py -3.12 ..\ops\watchdog\run.py check --notify
```

Resend requires a **verified domain** (or Resend's test sender) for `EMAIL_FROM`. A 403 usually means domain/from mismatch — not a missing code path.
