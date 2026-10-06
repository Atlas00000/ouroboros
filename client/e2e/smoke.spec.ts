import { expect, test } from "@playwright/test";

test.describe("Ouroboros client smoke", () => {
  test("sign-in gate page renders without Clerk keys", async ({ page }) => {
    await page.goto("/sign-in");
    await expect(page.getByRole("heading", { name: "Sign-in unavailable" })).toBeVisible();
    await expect(page.getByText("NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY")).toBeVisible();
  });

  test("home loads chrome and masthead", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("link", { name: "Skip to content" })).toBeAttached();
    await expect(page.getByRole("navigation", { name: "Primary" })).toBeVisible();
    await expect(page.getByRole("link", { name: "Home" })).toBeVisible();
    await expect(page.getByRole("link", { name: "News" })).toBeVisible();
    await expect(page.getByRole("link", { name: "Scoring" })).toBeVisible();
    await expect(page.getByRole("link", { name: "Desk" })).toBeVisible();
    await expect(page.getByRole("button", { name: /switch to (light|dark) theme/i })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Ouroboros", level: 1 })).toBeVisible();
    await expect(page.getByText(/research context only/i)).toBeVisible();
  });

  test("news scoring desk and asset routes render", async ({ page }) => {
    await page.goto("/news");
    await expect(page.getByRole("heading", { name: "News", level: 1 })).toBeVisible();

    await page.goto("/scoring");
    await expect(page.getByRole("heading", { name: "Scoring", level: 1 })).toBeVisible();

    await page.goto("/system");
    await expect(page.getByRole("heading", { name: "Desk", level: 1 })).toBeVisible();

    await page.goto("/assets/EURUSD");
    await expect(page.getByRole("heading", { name: "EURUSD", level: 1 })).toBeVisible();
    await expect(page.getByRole("link", { name: "← Home" })).toBeVisible();
  });
});
