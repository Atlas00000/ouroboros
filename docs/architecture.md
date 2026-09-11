# High-level architecture (Phase 0 stub)

See [roadmap.md](../roadmap.md) §§3–4 and [adr/](./adr/).

```
client/ (Vercel)  --HTTPS-->  server API (Railway)
                                  |
                    +-------------+-------------+
                    |             |             |
              TimescaleDB      Redis         worker
              (prices,         (cache +      (scheduler)
               profiles,        Streams)
               outbox)
                    ^
                    |
              MT5 Windows worker (Phase 1)
```

Auth: Clerk JWT (humans) or API key (machines). Email: Resend.
