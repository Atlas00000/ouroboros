import { defineConfig, devices } from "@playwright/test";

const PORT = Number(process.env.PLAYWRIGHT_PORT || 3000);
const baseURL = process.env.PLAYWRIGHT_BASE_URL || `http://127.0.0.1:${PORT}`;

/** Prefer system Chrome when Playwright's bundled browser cannot be downloaded. */
const useSystemChrome = process.env.PLAYWRIGHT_USE_SYSTEM_CHROME === "1";

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: process.env.CI ? "github" : "list",
  use: {
    baseURL,
    trace: "on-first-retry",
    ...(useSystemChrome
      ? { channel: "chrome" as const }
      : devices["Desktop Chrome"]),
  },
  webServer: {
    command: `pnpm exec next start --hostname 127.0.0.1 --port ${PORT}`,
    url: baseURL,
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
