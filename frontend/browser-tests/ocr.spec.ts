import { test, expect } from "@playwright/test";
import { readFileSync, mkdirSync } from "node:fs";
import { imagePoint } from "./coordinates";
const net = JSON.parse(readFileSync("public/demos/mixed-network.json", "utf8"));
const image = readFileSync("public/demos/mixed-network.png");

for (const lang of ["en", "bn"])
  test(`inspect, assign, ignore and reread only a selected text crop (${lang})`, async ({
    page,
  }) => {
    await page.addInitScript(
      (value) => localStorage.setItem("circuit-language", value),
      lang,
    );
    await page.route("**/api/analyze/start", (r) =>
      r.fulfill({ json: { job_id: "ocr", width: 606, height: 366 } }),
    );
    await page.route("**/api/analyze/ocr", (r) =>
      r.fulfill({
        json: {
          stage: "done",
          stage_index: 8,
          elapsed_seconds: 1,
          error: null,
          partial: {},
          result: {
            netlist: net,
            solution: {},
            warnings: [],
            timings: { total: 1 },
            provenance: "extracted",
            diagnostics: {
              texts: [
                {
                  id: "t1",
                  text: "40 Q",
                  bbox: [150, 15, 200, 35],
                  confidence: 0.8,
                  parsed: { number: 40, unit: null },
                  outcome: "unassigned",
                  reason: "unit_mismatch",
                  engine: "rapidocr",
                  rotation: 180,
                  raw_text: "40 Q",
                  ocr_backend: "hybrid",
                  alternatives: [
                    {
                      text: "100 Ω",
                      confidence: 0.9,
                      engine: "easyocr-bn",
                      rotation: 0,
                      parsed: { number: 100, unit: "ohm" },
                    },
                  ],
                },
                {
                  id: "t2",
                  text: "E",
                  bbox: [280, 320, 300, 340],
                  confidence: 0.9,
                  parsed: { number: null, unit: null },
                  outcome: "unassigned",
                  reason: "label_type_mismatch",
                },
              ],
            },
          },
        },
      }),
    );
    let cropSize: [number, number] = [0, 0];
    let consent = "";
    await page.route("**/api/ocr-crop", (r) => {
      const body = r.request().postDataBuffer()!;
      const offset = body.indexOf(
        Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]),
      );
      cropSize = [
        body.readUInt32BE(offset + 16),
        body.readUInt32BE(offset + 20),
      ];
      consent = body.toString();
      return r.fulfill({
        json: {
          candidates: [
            {
              text: "3.0 v",
              confidence: 0.9,
              bbox: [0, 0, 45, 20],
              parsed: { number: 3, unit: "V" },
            },
          ],
          diagnostics: {},
          warnings: [],
        },
      });
    });
    await page.goto("/");
    await expect(page.locator("#readout tr")).toHaveCount(7);
    await page.locator("#upload").setInputFiles({
      name: "diagram.png",
      mimeType: "image/png",
      buffer: image,
    });
    await expect(page.getByTestId("provenance-banner")).toHaveClass(
      /extracted/,
    );
    await page.getByTestId("show-text").check();
    const canvas = page.locator("#overlay");
    const p = await imagePoint(page, 175, 25);
    await page.mouse.move(p.x, p.y);
    await expect(canvas).toHaveAttribute("title", /40 Q/);
    await page.mouse.click(p.x, p.y);
    await expect(page.getByTestId("text-popover")).toBeVisible();
    await expect(page.getByTestId("text-popover")).toContainText(
      "rapidocr · 180°",
    );
    await page
      .getByRole("button", { name: "100 Ω · easyocr-bn", exact: true })
      .click();
    await expect(page.getByTestId("ocr-value")).toHaveValue("100");
    await page.getByTestId("ocr-target").selectOption("R1");
    await page.getByTestId("ocr-value").fill("40");
    mkdirSync("../.cache/round3/ui", { recursive: true });
    await page.screenshot({
      path: `../.cache/round3/ui/ocr-${lang}.png`,
      fullPage: true,
    });
    await page.getByTestId("ocr-apply").click();
    await expect(page.locator("input[type=number][data-param=R1]")).toHaveValue(
      "40",
    );
    const q = await imagePoint(page, 290, 330);
    await page.mouse.click(q.x, q.y);
    await page
      .getByTestId("text-popover")
      .getByRole("button", {
        name: lang === "en" ? "Ignore" : "উপেক্ষা করুন",
        exact: true,
      })
      .click();
    await page.getByTestId("ocr-read-area").click();
    const a = await imagePoint(page, 150, 10),
      b = await imagePoint(page, 200, 35);
    await page.mouse.move(a.x, a.y);
    await page.mouse.down();
    await page.mouse.move(b.x, b.y, { steps: 6 });
    await page.mouse.up();
    await expect(page.getByTestId("text-popover")).toBeVisible();
    expect(cropSize[0]).toBeLessThan(55);
    expect(cropSize[0]).toBeGreaterThan(45);
    expect(cropSize[1]).toBeLessThan(30);
    expect(consent).toContain("false");
    await page.getByTestId("ocr-target").selectOption("V1");
    await page.getByTestId("ocr-apply").click();
    await expect(page.locator("input[type=number][data-param=V1]")).toHaveValue(
      "3",
    );
  });
