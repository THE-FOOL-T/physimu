import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdirSync, writeFileSync } from "node:fs";
// Use consistent CPU canvas rasterization for layout snapshots.
test.use({ launchOptions: { args: ["--disable-accelerated-2d-canvas"] } });

for (const [width, height] of [
  [1440, 900],
  [1024, 768],
  [390, 844],
])
  for (const lang of ["en", "bn"])
    for (const theme of ["light", "dark"]) {
      test(`workspace ${width} ${lang} ${theme}`, async ({ page }) => {
        await page.setViewportSize({ width, height });
        await page.emulateMedia({ reducedMotion: "reduce" });
        await page.addInitScript(
          ({ lang, theme }) => {
            localStorage.setItem("circuit-language", lang);
            localStorage.setItem("circuit-theme", theme);
          },
          { lang, theme },
        );
        await page.route("**/api/health", (r) =>
          r.fulfill({ json: { detector: "ready" } }),
        );
        await page.goto("/");
        await expect(page.locator("#overlay")).toHaveAttribute(
          "data-image-ready",
          "true",
        );
        await expect(page.locator("#readout tr")).toHaveCount(7);
        await page.locator("#play").click();
        await page.evaluate(() => document.fonts.ready);
        await page.locator("#overlay").scrollIntoViewIfNeeded();
        await expect
          .poll(() =>
            page
              .locator("#canvas-viewport")
              .evaluate((e) => e.scrollHeight - e.clientHeight),
          )
          .toBeLessThanOrEqual(1);
        // Complete canvas readback before full-page capture.
        await page.locator("#overlay").evaluate((c) => c.toDataURL());
        expect(
          await page.evaluate(
            () => document.documentElement.scrollWidth <= innerWidth,
          ),
        ).toBe(true);
        expect(
          await page
            .locator(".workspace-tabs:visible button")
            .evaluateAll((buttons) =>
              buttons.every(
                (button) => button.scrollWidth <= button.clientWidth + 1,
              ),
            ),
        ).toBe(true);
        await expect(page.locator("#controls .part-icon")).toHaveCount(7);
        await expect(page).toHaveScreenshot(`${width}-${lang}-${theme}.png`, {
          fullPage: true,
          animations: "disabled",
          mask: [page.locator("#solve-time")],
          maxDiffPixelRatio: 0,
        });
        const report = await new AxeBuilder({ page })
          .withTags(["wcag2a", "wcag2aa"])
          .analyze();
        mkdirSync("../docs/ui/accessibility", { recursive: true });
        writeFileSync(
          `../docs/ui/accessibility/${width}-${lang}-${theme}.json`,
          JSON.stringify(
            {
              critical: report.violations.filter((v) => v.impact === "critical")
                .length,
              violations: report.violations.map((v) => ({
                id: v.id,
                impact: v.impact,
                nodes: v.nodes.map((n) => n.target),
              })),
            },
            null,
            2,
          ),
        );
        expect(
          report.violations.filter((v) => v.impact === "critical"),
        ).toEqual([]);
      });
    }
test("keyboard operation reaches upload, playback, part selection and value editing", async ({
  page,
}) => {
  await page.goto("/");
  await expect(page.locator("#readout tr")).toHaveCount(7);
  await page.locator("#dropzone").focus();
  const chooser = page.waitForEvent("filechooser");
  await page.keyboard.press("Enter");
  await chooser;
  await page.locator("#play").focus();
  await page.keyboard.press("Enter");
  await expect(page.locator("#play")).toHaveText("Play");
  await page.locator("#overlay").focus();
  await page.keyboard.press("ArrowRight");
  await expect(page.locator("[data-tab=readouts]")).toHaveAttribute(
    "aria-selected",
    "true",
  );
  await page.locator("[data-tab=parameters]").click();
  const before = await page.locator("#supplied").textContent();
  await page.locator("input[type=number][data-param=R1]").focus();
  await page.keyboard.press("ControlOrMeta+A");
  await page.keyboard.type("2000");
  await expect(page.locator("#supplied")).not.toHaveText(before!);
  await page.locator("#edit").focus();
  await page.keyboard.press("Enter");
  await expect(page.locator(".editing-badge")).toBeVisible();
});
