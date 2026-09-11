# Cloudflare / Wrangler (optional)

Installed at monorepo root via pnpm (`wrangler` in `package.json`).

```bash
pnpm install
pnpm wrangler login
pnpm wrangler:whoami
```

Hosting of record for this project remains **Vercel + Railway**. Wrangler is wired so Cloudflare Workers/R2 can be added without a later monorepo refactor.
