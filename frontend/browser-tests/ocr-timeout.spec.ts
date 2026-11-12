import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";

const fixture = JSON.parse(
  readFileSync("public/demos/mixed-network.json", "utf8"),
);
const image = readFileSync("public/demos/mixed-network.png");

for (const lang of ["en", "bn"]) {
  for (const status of ["timeout", "limited"]) {
    test(`incomplete tracing and OCR time limits explain the result (${lang}, ${status})`, async ({
      page,
    }) => {
      const net = structuredClone(fixture);
      net.components[0].value.status = "assumed";
      await page.addInitScript(
        (value) => localStorage.setItem("circuit-language", value),
        lang,
      );
      await page.route("**/api/analyze/start", (route) =>
        route.fulfill({ json: { job_id: "limited", width: 606, height: 366 } }),
      );
      await page.route("**/api/analyze/limited", (route) =>
        route.fulfill({
          json: {
            stage: "done",
            stage_index: 8,
            elapsed_seconds: 15,
            error: null,
            partial: {},
            result: {
              netlist: net,
              solution: {},
              warnings: [],
              timings: { total: 15 },
              provenance: "partial",
              diagnostics: {
                texts: [],
                trace: { budget_exceeded: true },
                stages: [{ stage: "easyocr-bn", status }],
              },
            },
          },
        }),
      );
      await page.goto("/");
      await page.locator("#upload").setInputFiles({
        name: "diagram.png",
        mimeType: "image/png",
        buffer: image,
      });
      const banner = page.getByTestId("provenance-banner");
      await expect(banner).toContainText(
        lang === "en"
          ? "Wire tracing did not finish"
          : "তার শনাক্তকরণ শেষ হয়নি",
      );
      await expect(banner).toContainText(
        lang === "en"
          ? "Completed readings were kept"
          : "পড়া তথ্য রাখা হয়েছে",
      );
      await expect(banner).toContainText(
        lang === "en" ? "assumed values" : "অনুমিত মান",
      );
    });
  }
}
