import { test, expect } from "@playwright/test";
import { mkdirSync, readFileSync } from "node:fs";

test("PNG export matches the complete displayed canvas", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/");
  const canvas = page.locator("#overlay");
  await expect(canvas).toHaveAttribute("data-image-ready", "true");
  await expect(page.locator("#readout tr")).toHaveCount(7);
  const size = await canvas.evaluate((c: HTMLCanvasElement) => ({
    width: c.width,
    height: c.height,
  }));
  const [download] = await Promise.all([
    page.waitForEvent("download"),
    page.locator("#export").click(),
  ]);
  const bytes = readFileSync((await download.path())!);
  expect(bytes.subarray(1, 4).toString()).toBe("PNG");
  expect(bytes.readUInt32BE(16)).toBe(size.width);
  expect(bytes.readUInt32BE(20)).toBe(size.height);
  expect(bytes.length).toBeGreaterThan(10_000);
  mkdirSync("../.cache/round3/ui", { recursive: true });
  await download.saveAs("../.cache/round3/ui/export-final.png");
});
