import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
const net = JSON.parse(readFileSync("public/demos/mixed-network.json", "utf8"));
const image = readFileSync("public/demos/mixed-network.png");

test("immediate receipt, real job stages, partial preview and extracted summary", async ({
  page,
}) => {
  let index = 0;
  const stages = [
    "received",
    "preprocess",
    "detect",
    "text",
    "wires",
    "validate",
    "resolve",
    "solve",
    "done",
  ];
  await page.route("**/api/analyze/start", (route) =>
    route.fulfill({
      json: { job_id: "slow", width: 606, height: 366, page_count: 1 },
    }),
  );
  await page.route("**/api/analyze/slow", (route) => {
    const i = Math.min(index++, 8);
    return route.fulfill({
      json: {
        stage: stages[i],
        stage_index: i,
        stage_count: 9,
        elapsed_seconds: i * 0.4,
        error: null,
        partial:
          i >= 3
            ? {
                components: net.components,
                source_image: "/demos/mixed-network.png",
              }
            : {},
        result:
          i === 8
            ? {
                netlist: net,
                solution: {},
                warnings: [],
                provenance: "extracted",
                timings: { total: 3.2 },
              }
            : null,
      },
    });
  });
  await page.goto("/");
  await expect(page.locator("#readout tr")).toHaveCount(7);
  const received = await page.evaluate(async () => {
    const input = document.querySelector<HTMLInputElement>("#upload")!;
    const dt = new DataTransfer();
    dt.items.add(
      new File([new Uint8Array([1, 2, 3])], "receipt.png", {
        type: "image/png",
      }),
    );
    input.files = dt.files;
    const start = performance.now();
    input.dispatchEvent(new Event("change", { bubbles: true }));
    await Promise.resolve();
    await Promise.resolve();
    return {
      ms: performance.now() - start,
      text: document.querySelector("[data-testid=upload-receipt]")!.textContent,
    };
  });
  expect(received.ms).toBeLessThan(200);
  expect(received.text).toContain("Uploaded");
  await expect(page.getByTestId("analysis-stepper")).toBeVisible({
    timeout: 1000,
  });
  await expect(page.locator(".stepper [aria-current=step]")).toHaveText(
    "Received",
  );
  await expect(page.getByTestId("detected-preview")).toBeVisible();
  await expect(page.getByTestId("provenance-banner")).toHaveClass(/extracted/);
  await expect(page.getByTestId("result-summary")).toContainText(
    "Found 7 components",
  );
  expect(index).toBe(9);
});

test("missing weights fallback is red and separated from uploaded geometry", async ({
  page,
}) => {
  const demo = structuredClone(net);
  demo.image.path = "";
  demo.meta.provenance = "demo_fallback";
  await page.route("**/api/analyze/start", (r) =>
    r.fulfill({
      json: { job_id: "fail", width: 606, height: 366, page_count: 1 },
    }),
  );
  await page.route("**/api/analyze/fail", (r) =>
    r.fulfill({
      json: {
        stage: "done",
        stage_index: 8,
        elapsed_seconds: 0.1,
        partial: {},
        error: null,
        result: {
          netlist: demo,
          solution: {},
          provenance: "demo_fallback",
          timings: { total: 0.1 },
          warnings: [
            {
              code: "detector_unavailable",
              message_key: "warn.detector_unavailable",
            },
          ],
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
  await expect(page.getByTestId("provenance-banner")).toHaveClass(
    /demo_fallback/,
  );
  await expect(page.getByTestId("provenance-banner")).toContainText(
    "Detector model not installed",
  );
  await expect(page.locator("#overlay")).toHaveAttribute(
    "data-provenance",
    "demo_fallback",
  );
  await page
    .getByTestId("import-strip")
    .getByRole("button", { name: "Expand import" })
    .click();
  await expect(page.getByTestId("upload-preview")).toBeVisible();
  await expect(page.locator("#circuit-title")).toContainText("Demo");
});

for (const language of ["en", "bn"])
  test(`readable invalid upload errors and retry (${language})`, async ({
    page,
  }) => {
    await page.addInitScript(
      (lang) => localStorage.setItem("circuit-language", lang),
      language,
    );
    await page.goto("/");
    await page.locator("#upload").setInputFiles({
      name: "bad.txt",
      mimeType: "text/plain",
      buffer: Buffer.from("text"),
    });
    await expect(page.getByTestId("upload-error")).toContainText(
      language === "en" ? "Unsupported file" : "সমর্থিত নয়",
    );
    await page.locator("#upload").setInputFiles({
      name: "huge.png",
      mimeType: "image/png",
      buffer: Buffer.alloc(20 * 1024 * 1024 + 1),
    });
    await expect(page.getByTestId("upload-error")).toContainText(
      language === "en" ? "too large" : "ফাইলটি বড়",
    );
    await expect(page.locator("#readout tr")).toHaveCount(7);
    await expect(
      page
        .getByTestId("upload-error")
        .locator("..")
        .getByText(language === "en" ? "Retry" : "আবার চেষ্টা", {
          exact: true,
        }),
    ).toBeVisible();
  });
