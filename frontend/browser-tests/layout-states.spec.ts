import { test, expect } from "@playwright/test";
import { mkdirSync, readFileSync } from "node:fs";
import { imagePoint } from "./coordinates";
const net = JSON.parse(readFileSync("public/demos/mixed-network.json", "utf8"));
const image = readFileSync("public/demos/mixed-network.png");

for (const [width, height] of [
  [1440, 1000],
  [1024, 900],
  [390, 844],
])
  for (const lang of ["en", "bn"]) {
    test(`import, fit and every editor tool ${width} ${lang}`, async ({
      page,
    }) => {
      test.setTimeout(90000);
      const folder = "../.cache/round3/ui/layout-state";
      mkdirSync(folder, { recursive: true });
      await page.setViewportSize({ width, height });
      await page.emulateMedia({ reducedMotion: "reduce" });
      await page.addInitScript(
        (lang) => localStorage.setItem("circuit-language", lang),
        lang,
      );
      let complete = false;
      await page.route("**/api/analyze/start", (r) =>
        r.fulfill({ json: { job_id: "layout", width: 606, height: 366 } }),
      );
      await page.route("**/api/analyze/layout", (r) =>
        r.fulfill({
          json: {
            stage: complete ? "done" : "text",
            stage_index: complete ? 8 : 3,
            elapsed_seconds: 1,
            error: null,
            partial: {
              source_image: "/demos/mixed-network.png",
              components: net.components,
            },
            result: complete
              ? {
                  netlist: net,
                  solution: {},
                  warnings: [
                    {
                      code: "image_edge_cut",
                      ref: null,
                      message_key: "warn.image_edge_cut",
                    },
                  ],
                  timings: { total: 1 },
                  provenance: "extracted",
                }
              : null,
          },
        }),
      );
      const capture = async (state: string) => {
        await page.evaluate(() => document.fonts.ready);
        expect(
          await page.evaluate(
            () => document.documentElement.scrollWidth <= innerWidth,
          ),
        ).toBe(true);
        await page.screenshot({
          path: `${folder}/${width}-${lang}-${state}.png`,
          fullPage: true,
          animations: "disabled",
        });
      };
      await page.goto("/");
      await expect(page.locator("#controls .control")).toHaveCount(7);
      await page.locator("#play").click();
      await expect(page.locator("[data-tab=parameters]")).toHaveAttribute(
        "aria-selected",
        "true",
      );
      await expect(page.locator(".workspace-tabs button")).toHaveCount(4);
      if (width >= 1200) {
        const control = await page.locator("#controls").boundingBox(),
          canvas = await page.locator("#overlay").boundingBox();
        expect(control!.x).toBeGreaterThan(canvas!.x + canvas!.width);
      }
      await capture("idle");
      const fullName = "a".repeat(90) + ".png";
      await page.locator("#upload").setInputFiles({
        name: fullName,
        mimeType: "image/png",
        buffer: image,
      });
      await expect(page.getByTestId("analysis-stepper")).toBeVisible();
      await capture("analyzing");
      complete = true;
      await expect(page.getByTestId("import-strip")).toBeVisible();
      await expect(page.locator("#circuit-title")).toHaveText(
        lang === "en" ? "Uploaded diagram" : "আপলোড করা চিত্র",
      );
      await expect(page.locator("#circuit-title")).toHaveAttribute(
        "title",
        fullName,
      );
      await expect(page.locator(".image-edge-notice")).toBeVisible();
      const source = page.getByTestId("source-slider"),
        before = await page.locator("#supplied").textContent();
      await source.fill("10");
      await expect(page.locator("#supplied")).not.toHaveText(before!);
      await expect(
        page.locator("input[type=number][data-param=V1]"),
      ).toHaveValue("10");
      await capture("result");
      await page
        .getByTestId("import-strip")
        .getByRole("button", {
          name: lang === "en" ? "Show original" : "মূল ছবি দেখুন",
          exact: true,
        })
        .click();
      await expect(page.locator("dialog img")).toHaveJSProperty(
        "naturalWidth",
        606,
      );
      await page.locator("dialog button").click();
      await page.locator("#edit").click();
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
        // Fit always includes native corners, including with the tool rail visible.
        const a = await imagePoint(page, 0, 0),
          b = await imagePoint(page, 606, 366),
          bounds = (await page.locator("#overlay").boundingBox())!;
        expect(a.x - bounds.x).toBeGreaterThanOrEqual(23.9);
        expect(a.y - bounds.y).toBeGreaterThanOrEqual(23.9);
        expect(bounds.x + bounds.width - b.x).toBeGreaterThanOrEqual(23.9);
        expect(bounds.y + bounds.height - b.y).toBeGreaterThanOrEqual(23.9);
        await capture(tool);
      }
      await page.locator("[data-canvas-tool=select]").click();
      const p = await imagePoint(page, 180, 46);
      await page.mouse.click(p.x, p.y);
      await expect(page.getByTestId("part-popover")).toBeVisible();
      await capture("popover");
    });
  }

test("edge-to-edge source pixels survive Fit and drop-zone text wraps at 320px", async ({
  page,
}) => {
  await page.setViewportSize({ width: 320, height: 844 });
  await page.goto("/");
  await expect(page.locator("#controls .control")).toHaveCount(7);
  expect(
    await page
      .locator(".dropzone")
      .evaluate(
        (e) =>
          e.scrollHeight <= e.clientHeight && e.scrollWidth <= e.clientWidth,
      ),
  ).toBe(true);
  const edged = structuredClone(net);
  edged.image = {
    width: 606,
    height: 366,
    path:
      "data:image/svg+xml," +
      encodeURIComponent(
        '<svg xmlns="http://www.w3.org/2000/svg" width="606" height="366"><rect width="606" height="366" fill="white"/><path d="M0 0H606V366H0Z" fill="none" stroke="black" stroke-width="4"/></svg>',
      ),
  };
  await page.locator("#json-upload").setInputFiles({
    name: "Edges.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(edged)),
  });
  await page.locator("#label-mode").selectOption("off");
  await page.locator("#play").click();
  await imagePoint(page, 0, 0);
  await expect
    .poll(() =>
      page.locator("#overlay").evaluate((c) => {
        const ctx = c.getContext("2d")!,
          dpr = c.width / c.clientWidth,
          s = Number(c.dataset.viewScale),
          x = Number(c.dataset.viewX),
          y = Number(c.dataset.viewY);
        return [
          [1, 1],
          [605, 1],
          [1, 365],
          [605, 365],
        ].every(([a, b]) => {
          const pixels = ctx.getImageData(
            Math.round((x + a * s) * dpr) - 1,
            Math.round((y + b * s) * dpr) - 1,
            3,
            3,
          ).data;
          return [...pixels].some(
            (value, index) => index % 4 === 0 && value < 220,
          );
        });
      }),
    )
    .toBe(true);
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
});
