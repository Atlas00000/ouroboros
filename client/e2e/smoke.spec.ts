import { expect, test } from "@playwright/test";

test.describe("Ouroboros client smoke", () => {
  test("sign-in gate page renders without Clerk keys", async ({ page }) => {
    await page.goto("/sign-in");
    await expect(page.getByRole("heading", { name: "Sign-in unavailable" })).toBeVisible();
    await expect(page.getByText("NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY")).toBeVisible();
  });

  test("dashboard loads primary landmark", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("link", { name: "Skip to content" })).toBeAttached();
    await expect(page.getByRole("heading", { name: "Ouroboros", level: 1 })).toBeVisible();
    await expect(page.getByRole("navigation", { name: "Primary" })).toBeVisible();
    await expect(page.getByText(/research context only/i)).toBeVisible();
  });

  test("asset detail route renders sticky symbol chrome", async ({ page }) => {
    await page.goto("/assets/EURUSD");
    await expect(page.getByRole("heading", { name: "EURUSD", level: 1 })).toBeVisible();
    await expect(page.getByRole("link", { name: "← Dashboard" })).toBeVisible();
  });

  test("System role-denied when e2e_role=viewer", async ({ context, page }) => {
    await context.addCookies([
      {
        name: "e2e_role",
        value: "viewer",
        url: "http://127.0.0.1:3000",
      },
    ]);
    await page.goto("/system");
    await expect(page.getByRole("heading", { name: "Access denied" })).toBeVisible();
    await expect(page.getByText(/requires role/i)).toBeVisible();
    // Nav should hide System/Admin for viewer
    await expect(page.getByRole("navigation", { name: "Primary" }).getByRole("link", { name: "System" })).toHaveCount(0);
  });
});
