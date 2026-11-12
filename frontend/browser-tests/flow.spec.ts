import { test, expect, type Page } from "@playwright/test";
import { existsSync, mkdirSync, readFileSync } from "node:fs";

const directory = "../.cache/round3/ui/flow";
test.use({ launchOptions: { args: ["--disable-accelerated-2d-canvas"] } });
async function ready(page: Page, theme = "light") {
  await page.addInitScript(
    (theme) => localStorage.setItem("circuit-theme", theme),
    theme,
  );
  await page.goto("/");
  await expect(page.locator("#overlay")).toHaveAttribute(
    "data-image-ready",
    "true",
  );
  await expect
    .poll(async () =>
      Number(
        await page.locator("#overlay").getAttribute("data-flow-particles"),
      ),
    )
    .toBeGreaterThan(0);
}
async function capture(page: Page, name: string) {
  mkdirSync(directory, { recursive: true });
  await page
    .locator("#stage-area")
    .screenshot({ path: `${directory}/${name}.png` });
}
for (const theme of ["light", "dark"])
  test(`visible flow presets on the example in ${theme}`, async ({ page }) => {
    await ready(page, theme);
    await page.locator("#play").click();
    for (const style of ["dots", "dashes", "arrows", "glow"]) {
      await page.locator(".flow-controls summary").click();
      await page.getByTestId("flow-style").selectOption(style);
      await page.locator(".flow-options button").click();
      await capture(page, `${theme}-${style}`);
    }
    await page.locator(".flow-controls summary").click();
    await page.getByTestId("flow-color").selectOption("cyan");
    await page.getByTestId("flow-size").fill("2");
    await page.reload();
    await page.locator(".flow-controls summary").click();
    await expect(page.getByTestId("flow-style")).toHaveValue("glow");
    await expect(page.getByTestId("flow-color")).toHaveValue("cyan");
    await expect(page.getByTestId("flow-size")).toHaveValue("2");
  });

test("reference follows slider changes, zero current is explicit, reduced motion is static", async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await ready(page);
  const canvas = page.locator("#overlay");
  const before = Number(await canvas.getAttribute("data-flow-reference"));
  await page.getByTestId("source-slider").fill("4");
  await expect
    .poll(async () => Number(await canvas.getAttribute("data-flow-reference")))
    .toBeLessThan(before * 0.5);
  const pixels = await canvas.evaluate((c: HTMLCanvasElement) => c.toDataURL());
  await page.waitForTimeout(150);
  expect(await canvas.evaluate((c: HTMLCanvasElement) => c.toDataURL())).toBe(
    pixels,
  );
  await capture(page, "reduced-static-arrows");
  await page.getByTestId("source-slider").fill("0");
  await expect(canvas).toHaveAttribute("data-flow-particles", "0");
  await expect(page.getByTestId("flow-state")).toContainText("No current");
  await capture(page, "zero-current");
});

test("short circuit uses a distinct magenta path", async ({ page }) => {
  await ready(page);
  const net = JSON.parse(
    readFileSync("../fixtures/source_short.json", "utf8"),
  ).netlist;
  await page.locator("#json-upload").setInputFiles({
    name: "Short circuit.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(net)),
  });
  await expect(page.locator("#controls .control")).toHaveCount(2);
  await expect(page.locator("#overlay")).toHaveAttribute(
    "data-flow-state",
    "flowing",
  );
  await page.locator("#play").click();
  await capture(page, "short-circuit");
});

for (const theme of ["light", "dark"])
  test(`real owner analysis shows flow in ${theme}`, async ({ page }) => {
    const path = existsSync("../.cache/round3/engine-final.json")
      ? "../.cache/round3/engine-final.json"
      : "../.cache/round3/engine-b.json";
    test.skip(
      !existsSync(path),
      "Owner response stays in the ignored local cache.",
    );
    await ready(page, theme);
    const result = JSON.parse(readFileSync(path, "utf8"));
    const net = result.netlist;
    await page.locator("#json-upload").setInputFiles({
      name: "Owner 24V analysis.json",
      mimeType: "application/json",
      buffer: Buffer.from(JSON.stringify(net)),
    });
    await expect(page.locator("#controls .control")).toHaveCount(
      net.components.length,
    );
    await expect(page.locator("#overlay")).toHaveAttribute(
      "data-image-ready",
      "true",
    );
    await expect
      .poll(async () =>
        Number(
          await page.locator("#overlay").getAttribute("data-flow-particles"),
        ),
      )
      .toBeGreaterThan(0);
    await page.locator("#play").click();
    await capture(page, `owner-${theme}`);
  });
