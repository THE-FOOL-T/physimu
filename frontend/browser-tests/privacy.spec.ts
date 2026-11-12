import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
const net = JSON.parse(readFileSync("public/demos/mixed-network.json", "utf8"));
test("AI reader is off by default, disclosed before opt-in, and style can be overridden", async ({
  page,
}) => {
  const requests: { reader: string; style: string }[] = [];
  await page.route("**/api/analyze/start", (route) => {
    const body = route.request().postData() || "";
    const field = (name: string) =>
      body.match(new RegExp(`name="${name}"\\r\\n\\r\\n([^\\r]+)`))?.[1] || "";
    requests.push({ reader: field("use_label_reader"), style: field("style") });
    return route.fulfill({
      json: { job_id: "privacy", width: 606, height: 366, page_count: 1 },
    });
  });
  await page.route("**/api/analyze/privacy", (route) =>
    route.fulfill({
      json: {
        stage: "done",
        stage_index: 8,
        elapsed_seconds: 0.1,
        partial: {},
        error: null,
        result: {
          netlist: net,
          solution: {},
          provenance: "extracted",
          warnings: [],
          timings: { total: 0.1 },
          style_estimate: {
            style: "printed",
            effective_style:
              requests.at(-1)?.style === "handwritten"
                ? "handwritten"
                : "printed",
            confidence: 0.55,
            override: requests.at(-1)?.style !== "auto",
          },
        },
      },
    }),
  );
  await page.goto("/");
  await expect(page.locator("#readout tr")).toHaveCount(7);
  await expect(page.getByTestId("ai-reader")).not.toBeChecked();
  await expect(page.locator("#style")).toHaveValue("auto");
  const file = {
    name: "diagram.png",
    mimeType: "image/png",
    buffer: readFileSync("public/demos/mixed-network.png"),
  };
  await page.locator("#upload").setInputFiles(file);
  await expect(page.getByTestId("result-summary")).toContainText(
    "Estimated style: Printed",
  );
  expect(requests[0]).toEqual({ reader: "false", style: "auto" });
  await page
    .getByTestId("import-strip")
    .getByRole("button", { name: "Expand import" })
    .click();
  await page.getByTestId("reader-settings").locator("summary").click();
  await expect(page.locator(".reader-disclosure")).toContainText(
    "only cropped label regions",
  );
  await page.getByTestId("ai-reader").check();
  await page.locator("#style").selectOption("handwritten");
  await page.locator("#upload").setInputFiles([]);
  await page.locator("#upload").setInputFiles(file);
  await expect(page.getByTestId("result-summary")).toContainText(
    "Style override: Handwritten",
  );
  expect(requests[1]).toEqual({ reader: "true", style: "handwritten" });
});
