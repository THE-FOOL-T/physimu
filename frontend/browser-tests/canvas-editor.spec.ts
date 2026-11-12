import { test, expect, type Page } from "@playwright/test";
import { readFileSync, mkdirSync, writeFileSync } from "node:fs";
import { cutWire, removeComponent } from "../src/ui/edit-geometry";
import type { Netlist } from "../src/types";
import { imagePoint } from "./coordinates";
const fixture = () =>
  JSON.parse(readFileSync("../fixtures/editor_loop.json", "utf8"))
    .netlist as Netlist;
async function load(page: Page, net: Netlist, lang = "en") {
  await page.addInitScript(
    (lang) => localStorage.setItem("circuit-language", lang),
    lang,
  );
  await page.goto("/");
  await expect(page.locator("#readout tr")).toHaveCount(7);
  await page.locator("#json-upload").setInputFiles({
    name: "Practice circuit.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(net)),
  });
  await expect(page.locator("#controls .control")).toHaveCount(
    net.components.length,
  );
}
async function point(page: Page, x: number, y: number) {
  return imagePoint(page, x, y);
}
async function click(page: Page, x: number, y: number) {
  const p = await point(page, x, y);
  await page.mouse.click(p.x, p.y);
}
async function drag(page: Page, a: [number, number], b: [number, number]) {
  const p = await point(page, ...a),
    q = await point(page, ...b);
  await page.mouse.move(p.x, p.y);
  await page.mouse.down();
  await page.mouse.move(q.x, q.y, { steps: 8 });
  await page.mouse.up();
}
test("two clicks close a missing wire; draft freezes; Run, undo/redo and compare work", async ({
  page,
}) => {
  const net = fixture();
  cutWire(net, "w1");
  await load(page, net);
  const frozen = await page.locator("#supplied").textContent();
  await page.locator("#edit").click();
  await expect(page.getByTestId("edit-runbar")).toContainText(
    "not simulated yet",
  );
  await page.getByTestId("run-edited").click();
  await expect(page.locator(".editing-badge")).toContainText("not simulated");
  await page.locator("[data-canvas-tool=wire]").click();
  await click(page, 100, 180);
  await click(page, 280, 100);
  await expect(page.getByTestId("precheck")).toHaveClass(/ready/);
  await expect(page.locator("#supplied")).toHaveText(frozen!);
  await page.keyboard.press("ControlOrMeta+Enter");
  await expect(page.locator("#app")).toHaveAttribute(
    "data-provenance",
    "edited",
  );
  await expect(page.getByTestId("edit-runbar")).toContainText(
    "Simulation of your edited diagram",
  );
  await expect(page.locator("#supplied")).not.toHaveText(frozen!);
  await page.getByTestId("compare-auto").click();
  await expect(page.getByTestId("compare-auto")).toHaveAttribute(
    "aria-pressed",
    "true",
  );
  await page.locator("[data-edit-again]").click();
  await page.locator("#undo").click();
  await expect(page.getByTestId("precheck")).not.toHaveClass(/ready/);
  await page.locator("#redo").click();
  await expect(page.getByTestId("precheck")).toHaveClass(/ready/);
});
test("draw a missed resistor rectangle, type 220 and run the edited circuit", async ({
  page,
}) => {
  const net = fixture();
  removeComponent(net, "R1");
  await load(page, net);
  await page.locator("#edit").click();
  await page.locator("[data-canvas-tool=add]").click();
  await drag(page, [280, 88], [340, 112]);
  await expect(page.getByTestId("part-popover")).toBeVisible();
  await page.locator("#part-value").fill("220");
  await page.locator("#undo").click();
  await expect(page.locator("#part-value")).toHaveValue("100");
  await page.locator("#redo").click();
  await expect(page.locator("#part-value")).toHaveValue("220");
  await page.locator("#part-value").press("Enter");
  await expect(page.getByTestId("precheck")).toHaveClass(/ready/);
  await page.getByTestId("run-edited").click();
  await expect(page.locator("#readout tr")).toHaveCount(2);
  await expect(page.locator("#supplied")).not.toHaveText("0 W");
  const download = page.waitForEvent("download");
  await page.locator("#save").click();
  const stream = await (await download).createReadStream();
  const chunks: Buffer[] = [];
  for await (const chunk of stream!) chunks.push(chunk);
  const saved = JSON.parse(Buffer.concat(chunks).toString());
  expect(saved.meta.provenance).toBe("edited");
  expect(
    saved.components.find((c: { id: string }) => c.id === "R1").value,
  ).toMatchObject({ number: 220, status: "user", source: "user" });
});
test("drag an end, cut a wire and change type from the popover; each edit is reversible", async ({
  page,
}) => {
  await load(page, fixture());
  await page.locator("#edit").click();
  await drag(page, [280, 100], [480, 200]);
  await expect(page.getByTestId("precheck")).not.toHaveClass(/ready/);
  await page.locator("#undo").click();
  await expect(page.getByTestId("precheck")).toHaveClass(/ready/);
  await page.locator("#redo").click();
  await expect(page.getByTestId("precheck")).not.toHaveClass(/ready/);
  await page.locator("#undo").click();
  await page.locator("[data-canvas-tool=cut]").click();
  await click(page, 480, 200);
  await expect(page.getByTestId("precheck")).not.toHaveClass(/ready/);
  await page.locator("#undo").click();
  await expect(page.getByTestId("precheck")).toHaveClass(/ready/);
  await page.locator("[data-canvas-tool=select]").click();
  await click(page, 310, 100);
  await page.locator("[data-part-type=lamp]").click();
  await expect(page.locator("[data-part-type=lamp]")).toHaveAttribute(
    "aria-pressed",
    "true",
  );
  await page.locator("#undo").click();
  await page
    .locator("[data-testid=part-popover] button")
    .filter({ hasText: "Close" })
    .click();
  await click(page, 310, 100);
  await expect(page.locator("[data-part-type=resistor]")).toHaveAttribute(
    "aria-pressed",
    "true",
  );
});
test("student fixes a missing wire using only the stepper and checklist", async ({
  page,
}) => {
  const net = fixture();
  cutWire(net, "w1");
  await load(page, net);
  await page.locator("#edit").click();
  await page.locator('[data-fix-step="1"]').click();
  await page.locator("[data-tab=warnings]").click();
  await page.locator("[data-check=loose]").click();
  // The checklist starts at the first highlighted end; no toolbar knowledge needed.
  const label = await page.getByTestId("precheck").textContent();
  expect(label).toContain("Needs checking");
  await click(page, 100, 180);
  await expect(page.getByTestId("precheck")).toHaveClass(/ready/);
  await page.getByTestId("run-edited").click();
  await expect(page.locator("#app")).toHaveAttribute(
    "data-provenance",
    "edited",
  );
});
test("touch taps draw the missing wire on a phone", async ({ browser }) => {
  const context = await browser.newContext({
      hasTouch: true,
      viewport: { width: 390, height: 844 },
    }),
    page = await context.newPage();
  const net = fixture();
  cutWire(net, "w1");
  await load(page, net);
  await page.locator("#edit").tap();
  await page.locator("[data-canvas-tool=wire]").tap();
  for (const xy of [
    [100, 180],
    [280, 100],
  ]) {
    const p = await point(page, xy[0], xy[1]);
    await page.touchscreen.tap(p.x, p.y);
  }
  await expect(page.getByTestId("precheck")).toHaveClass(/ready/);
  await page.getByTestId("run-edited").tap();
  await expect(page.locator("#app")).toHaveAttribute(
    "data-provenance",
    "edited",
  );
  await context.close();
});
for (const lang of ["en", "bn"])
  test(`inspect every canvas tool and part popover ${lang}`, async ({
    page,
  }) => {
    await load(page, fixture(), lang);
    await page.locator("#edit").click();
    mkdirSync("../.cache/round3/ui/editor", { recursive: true });
    for (const tool of [
      "select",
      "wire",
      "cut",
      "add",
      "junction",
      "read",
      "pan",
    ]) {
      await page.locator(`[data-canvas-tool=${tool}]`).click();
      await page.locator(".center").screenshot({
        path: `../.cache/round3/ui/editor/${lang}-${tool}.png`,
        animations: "disabled",
      });
      await page.keyboard.press("Escape");
    }
    await page.locator("[data-canvas-tool=select]").click();
    await click(page, 310, 100);
    await page.screenshot({
      path: `../.cache/round3/ui/editor/${lang}-popover.png`,
      fullPage: true,
      animations: "disabled",
    });
  });

test("a typical edited Run validates, resolves and renders within 50 ms", async ({
  page,
}) => {
  await page.goto("/");
  await expect(page.locator("#readout tr")).toHaveCount(7);
  const samples = await page.evaluate(() => {
    const times: number[] = [];
    for (let i = 0; i < 30; i++) {
      document.getElementById("edit")!.click();
      const input = document.querySelector<HTMLInputElement>(
        "input[type=number][data-param=R1]",
      )!;
      input.value = String(5000 + i);
      input.dispatchEvent(new Event("input", { bubbles: true }));
      const start = performance.now();
      document
        .querySelector<HTMLButtonElement>("[data-testid=run-edited]")!
        .click();
      times.push(performance.now() - start);
    }
    return times.sort((a, b) => a - b);
  });
  const report = {
    samples: 30,
    median_ms: samples[15],
    p95_ms: samples[28],
    max_ms: samples[29],
    scope:
      "Seven-part example: synchronous Run event through topology, checks, constraint resolution, solve and readout DOM; excludes paint",
  };
  writeFileSync(
    "../docs/edit-performance.json",
    JSON.stringify(report, null, 2),
  );
  expect(report.p95_ms).toBeLessThan(50);
  await expect(page.locator("#app")).toHaveAttribute(
    "data-provenance",
    "edited",
  );
});
