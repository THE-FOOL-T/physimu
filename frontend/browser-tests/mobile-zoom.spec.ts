import { test, expect } from "@playwright/test";
import { mkdirSync } from "node:fs";
import { imagePoint } from "./coordinates";
test.use({
  viewport: { width: 390, height: 844 },
  hasTouch: true,
  isMobile: true,
});
for (const lang of ["en", "bn"])
  test(`phone pinch, Fit and flow controls remain usable ${lang}`, async ({
    page,
  }) => {
    await page.addInitScript(
      (lang) => localStorage.setItem("circuit-language", lang),
      lang,
    );
    await page.goto("/");
    await expect(page.locator("#readout tr")).toHaveCount(7);
    const canvas = page.locator("#overlay");
    await canvas.scrollIntoViewIfNeeded();
    const box = (await canvas.boundingBox())!,
      x = box.x + box.width / 2,
      y = box.y + box.height / 2;
    const cdp = await page.context().newCDPSession(page);
    const points = (spread: number) => [
      { x: x - spread, y, id: 1 },
      { x: x + spread, y, id: 2 },
    ];
    await cdp.send("Input.dispatchTouchEvent", {
      type: "touchStart",
      touchPoints: points(35),
    });
    await cdp.send("Input.dispatchTouchEvent", {
      type: "touchMove",
      touchPoints: points(70),
    });
    await cdp.send("Input.dispatchTouchEvent", {
      type: "touchEnd",
      touchPoints: [],
    });
    await expect.poll(() => page.locator("#zoom").inputValue()).toBe("200");
    await page.getByTestId("fit").click();
    await expect(page.locator("#zoom")).toHaveValue("100");
    await page.locator(".flow-controls summary").click();
    await page.getByTestId("flow-style").selectOption("arrows");
    await page.getByTestId("flow-color").selectOption("magenta");
    expect(
      await page.locator(".flow-options").evaluate((e) => {
        const r = e.getBoundingClientRect();
        return r.left >= 0 && r.right <= innerWidth && r.bottom <= innerHeight;
      }),
    ).toBe(true);
    mkdirSync("../.cache/round3/ui", { recursive: true });
    await page.screenshot({
      path: `../.cache/round3/ui/mobile-flow-${lang}.png`,
    });
    await page.locator(".flow-options button").click();
    await expect(page.locator(".flow-controls")).not.toHaveAttribute(
      "open",
      "",
    );
    const part = await imagePoint(page, 180, 46);
    await page.mouse.click(part.x, part.y);
    await expect(page.getByTestId("part-popover")).toBeVisible();
    await expect
      .poll(async () => {
        const sheet = (await page.getByTestId("part-popover").boundingBox())!;
        return page.locator("#overlay").evaluate((c, top) => {
          const bottom =
            c.getBoundingClientRect().top +
            Number(c.dataset.viewY) +
            56 * Number(c.dataset.viewScale);
          return bottom < top - 12 && bottom > 0;
        }, sheet.y);
      })
      .toBe(true);
    await page.screenshot({
      path: `../.cache/round3/ui/mobile-part-${lang}.png`,
    });
  });

test("warmup badge waits for the text reader", async ({ page }) => {
  await page.clock.install();
  let ready = false;
  await page.route("**/api/health", (r) =>
    r.fulfill({
      json: { detector: "ready", ocr: ready ? "ready" : "warming" },
    }),
  );
  await page.goto("/");
  await expect(page.locator("#api-state")).toContainText(
    "Warming detector and text reader",
  );
  ready = true;
  await page.clock.runFor(5001);
  await expect(page.locator("#api-state")).toHaveText("Models ready");
});
