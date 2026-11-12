import { test, expect } from "@playwright/test";
import { writeFileSync } from "node:fs";
test("image-aligned workspace, live parameter changes and bilingual readouts", async ({
  page,
}) => {
  await page.goto("/");
  await expect(page.locator("#controls .control")).toHaveCount(7);
  const before = await page.locator("#supplied").textContent();
  await page.locator("input[type=number][data-param=R1]").fill("10000");
  await expect(page.locator("#supplied")).not.toHaveText(before!);
  await expect(page.locator("[data-component=R1] .status")).toHaveText(
    "Edited",
  );
  await expect(page.locator("#readout tr")).toHaveCount(7);
  await page.locator("[data-tab=readouts]").click();
  expect(await page.locator(".readout-table").innerText()).toMatchSnapshot(
    "readout-en.txt",
  );
  await expect
    .poll(async () => {
      return page.locator("#overlay").evaluate((c) => Number(c.dataset.viewY));
    })
    .toBeGreaterThanOrEqual(24);
  await page.screenshot({
    path: "../docs/browser-desktop.png",
    fullPage: true,
  });
  await page.locator("#language").click();
  await expect(page.locator("h1")).toContainText("সার্কিট");
  await expect(page.locator("#readout tr")).toHaveCount(7);
  expect(await page.locator(".readout-table").innerText()).toMatchSnapshot(
    "readout-bn.txt",
  );
  await page.screenshot({ path: "../docs/browser-bangla.png", fullPage: true });
});
test("edit wrong/missing components and undo; short path and RC playback", async ({
  page,
}) => {
  await page.goto("/");
  await expect(page.locator("#readout tr")).toHaveCount(7);
  await page.locator("#edit").click();
  await page.locator(".edit-dock > details > summary").click();
  await page.locator("#component-select").selectOption("R1");
  await page.locator("#component-type").selectOption("lamp");
  await expect(page.locator("#component-type")).toHaveValue("lamp");
  await page.locator("#undo").click();
  await expect(page.locator("#component-type")).toHaveValue("resistor");
  await page.locator("[data-canvas-tool=add]").click();
  const box = await page.locator("#overlay").boundingBox();
  await page
    .locator("#overlay")
    .click({ position: { x: box!.width * 0.5, y: box!.height * 0.7 } });
  await page.locator("#part-value").press("Enter");
  await expect(page.locator("#controls .control")).toHaveCount(8);
  await expect(page.locator("#readout tr")).toHaveCount(7);
  await page.locator("#undo").click();
  await expect(page.locator("#readout tr")).toHaveCount(7);
  await page.getByTestId("run-edited").click();
  await expect(page.locator("#app")).toHaveAttribute(
    "data-provenance",
    "edited",
  );
  await page.locator("[data-tab=parameters]").click();
  await page.locator("[data-component=R1] [data-action=select]").click();
  await page.locator("#short-add").click();
  await expect(page.locator("#short-banner")).toContainText("Short-circuit");
  await page.locator("#short-add").click();
  await page.locator("#demo").selectOption("rc");
  await expect(page.locator("#analysis-mode")).toHaveValue("transient");
  await expect(page.locator("#controls .control")).toHaveCount(3);
  await expect(page.locator("#physical-time")).not.toHaveText("0 s");
  await page.locator("#play").click();
  const time = await page.locator("#physical-time").textContent();
  await page.waitForTimeout(100);
  await expect(page.locator("#physical-time")).toHaveText(time!);
});
test("mobile workspace and offline saved examples", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.route("**/api/**", (route) => route.abort());
  await page.goto("/");
  await expect(page.locator("#readout tr")).toHaveCount(7);
  await expect(page.locator("#footer")).toContainText("offline");
  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth > window.innerWidth,
  );
  expect(overflow).toBe(false);
  await page.screenshot({ path: "../docs/browser-mobile.png", fullPage: true });
});
test("parameter-to-readout latency stays below 50 ms", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("#readout tr")).toHaveCount(7);
  const samples = await page.evaluate(() => {
    const input = document.querySelector<HTMLInputElement>(
      "input[type=number][data-param=R1]",
    )!;
    const times: number[] = [];
    for (let i = 0; i < 100; i++) {
      const start = performance.now();
      input.value = String(5000 + i * 20);
      input.dispatchEvent(new Event("input", { bubbles: true }));
      times.push(performance.now() - start);
    }
    return times.sort((a, b) => a - b);
  });
  const result = {
    samples: samples.length,
    median_ms: samples[50],
    p95_ms: samples[95],
    max_ms: samples[99],
    scope:
      "Synchronous browser parameter event through solver and readout DOM update; excludes next paint",
  };
  writeFileSync("../docs/performance.json", JSON.stringify(result, null, 2));
  expect(result.p95_ms).toBeLessThan(50);
  await expect(page.locator("#supplied")).toHaveText(
    (await page.locator("#consumed").textContent())!,
  );
});
