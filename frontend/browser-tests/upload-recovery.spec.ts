import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
const image = readFileSync("public/demos/mixed-network.png");
const imageFile = { name: "diagram.png", mimeType: "image/png", buffer: image };
const dictionary = Object.fromEntries(
  ["en", "bn"].map((lang) => [
    lang,
    JSON.parse(readFileSync(`src/i18n/${lang}.json`, "utf8")),
  ]),
);

test("valid PNG receipt and decoded preview appear within 200 ms", async ({
  page,
}) => {
  await page.route("**/api/analyze/start", (r) =>
    r.fulfill({ status: 503, json: { detail: { code: "busy" } } }),
  );
  await page.goto("/");
  await expect(page.locator("#readout tr")).toHaveCount(7);
  const timing = await page.evaluate(async (base64) => {
    const bytes = Uint8Array.from(atob(base64), (c) => c.charCodeAt(0));
    const input = document.querySelector<HTMLInputElement>("#upload")!;
    const preview = document.querySelector<HTMLImageElement>(
      "[data-testid=upload-preview]",
    )!;
    const dt = new DataTransfer();
    dt.items.add(new File([bytes], "diagram.png", { type: "image/png" }));
    input.files = dt.files;
    const start = performance.now();
    const decoded = new Promise<void>((resolve) =>
      preview.addEventListener("load", () => resolve(), { once: true }),
    );
    input.dispatchEvent(new Event("change", { bubbles: true }));
    const receiptMs = performance.now() - start;
    const received = document.querySelector(
      "[data-testid=upload-receipt]",
    )!.textContent;
    await decoded;
    return {
      receiptMs,
      previewMs: performance.now() - start,
      received,
      width: preview.naturalWidth,
    };
  }, image.toString("base64"));
  expect(timing.receiptMs).toBeLessThan(200);
  expect(timing.previewMs).toBeLessThan(200);
  expect(timing.received).toContain("Uploaded");
  expect(timing.width).toBeGreaterThan(0);
  await expect(page.getByTestId("upload-receipt")).toContainText("606 × 366");
});

test("slow cancellation does not delay a replacement upload or Cancel feedback", async ({
  page,
}) => {
  let starts = 0;
  let finishDelete: () => void = () => {};
  const pendingDelete = new Promise<void>(
    (resolve) => (finishDelete = resolve),
  );
  await page.route("**/api/analyze/start", (r) =>
    r.fulfill({ json: { job_id: "job" + ++starts, width: 606, height: 366 } }),
  );
  await page.route("**/api/analyze/job*", async (r) => {
    if (r.request().method() === "DELETE") {
      await pendingDelete;
      await r.fulfill({ json: { cancelled: true } });
    } else
      await r.fulfill({
        json: {
          stage: "detect",
          stage_index: 2,
          elapsed_seconds: 1,
          partial: {},
          error: null,
          result: null,
        },
      });
  });
  await page.goto("/");
  try {
    await page.locator("#upload").setInputFiles(imageFile);
    await expect(page.locator(".stepper [aria-current=step]")).toHaveText(
      dictionary.en["stage.detect"],
    );
    await page
      .locator("#upload")
      .setInputFiles({ ...imageFile, name: "replacement.png" });
    await expect(page.getByTestId("upload-receipt")).toContainText(
      "replacement.png",
      { timeout: 200 },
    );
    await expect.poll(() => starts).toBe(2);
    await page.getByTestId("analysis-cancel").click();
    await expect(page.getByTestId("upload-error")).toHaveText(
      dictionary.en["error.cancelled"],
      { timeout: 200 },
    );
    await expect(page.getByTestId("analysis-stepper")).toBeHidden();
    await expect(page.locator("#readout tr")).toHaveCount(7);
  } finally {
    finishDelete();
  }
});

for (const lang of ["en", "bn"])
  test(`server and network failures preserve the simulation and allow Retry (${lang})`, async ({
    page,
  }) => {
    await page.addInitScript(
      (value) => localStorage.setItem("circuit-language", value),
      lang,
    );
    let code = "too_large";
    let status = 413;
    let network = false;
    await page.route("**/api/analyze/start", (r) =>
      network
        ? r.abort("failed")
        : r.fulfill({ status, json: { detail: { code } } }),
    );
    await page.goto("/");
    await expect(page.locator("#readout tr")).toHaveCount(7);
    for (const [nextCode, nextStatus] of [
      ["too_large", 413],
      ["unsupported_type", 415],
      ["undecodable", 415],
      ["invalid_page", 422],
      ["busy", 429],
      ["server_error", 500],
    ] as const) {
      code = nextCode;
      status = nextStatus;
      await page.locator("#upload").setInputFiles(imageFile);
      await expect(page.getByTestId("upload-error")).toHaveText(
        dictionary[lang]["error." + code],
      );
      await expect(page.locator("#readout tr")).toHaveCount(7);
    }
    network = true;
    await page
      .getByTestId("upload-error")
      .locator("..")
      .getByRole("button", {
        name: dictionary[lang]["upload.retry"],
        exact: true,
      })
      .click();
    await expect(page.getByTestId("upload-error")).toHaveText(
      dictionary[lang]["error.network"],
    );
  });

test("120 second timeout is readable and leaves the prior circuit available", async ({
  page,
}) => {
  await page.clock.install();
  await page.route("**/api/analyze/start", (r) =>
    r.fulfill({ json: { job_id: "timeout", width: 606, height: 366 } }),
  );
  await page.route("**/api/analyze/timeout", (r) =>
    r.fulfill({
      json: {
        stage: "text",
        stage_index: 3,
        elapsed_seconds: 119,
        partial: {},
        error: null,
        result: null,
      },
    }),
  );
  await page.goto("/");
  await expect(page.locator("#readout tr")).toHaveCount(7);
  await page.locator("#upload").setInputFiles(imageFile);
  await expect(page.locator(".stepper [aria-current=step]")).toHaveText(
    dictionary.en["stage.text"],
  );
  await page.clock.fastForward(120001);
  await expect(page.getByTestId("upload-error")).toHaveText(
    dictionary.en["error.timeout"],
  );
  await expect(page.locator("#readout tr")).toHaveCount(7);
});

test("PDF page spinner submits zero-based selected page and keeps preview dimensions", async ({
  page,
}) => {
  const pages: string[] = [];
  await page.route("**/api/analyze/start", (r) => {
    const body = r.request().postData()!;
    pages.push(body.match(/name="page"\r\n\r\n(\d+)/)![1]);
    return r.fulfill({
      json: { job_id: "pdf", width: 800, height: 1200, page_count: 3 },
    });
  });
  await page.route("**/api/analyze/pdf", (r) =>
    r.fulfill({
      json:
        r.request().method() === "DELETE"
          ? { cancelled: true }
          : {
              stage: "text",
              stage_index: 3,
              elapsed_seconds: 1,
              partial: { source_image: "/demos/mixed-network.png" },
              error: null,
              result: null,
            },
    }),
  );
  await page.goto("/");
  await page.locator("#upload").setInputFiles({
    name: "sheet.pdf",
    mimeType: "application/pdf",
    buffer: Buffer.from("%PDF-mocked"),
  });
  const spinner = page.getByTestId("pdf-page");
  await expect(spinner).toBeVisible();
  await spinner.fill("2");
  await spinner.dispatchEvent("change");
  await expect.poll(() => pages).toEqual(["0", "1"]);
  await expect(page.getByTestId("upload-preview")).toBeVisible();
  await expect(page.getByTestId("upload-receipt")).toContainText("800 × 1200");
});

test("clipboard images use the same immediate upload flow", async ({
  page,
}) => {
  await page.route("**/api/analyze/start", (r) =>
    r.fulfill({ status: 429, json: { detail: { code: "busy" } } }),
  );
  await page.goto("/");
  await page.evaluate(() => {
    const clipboardData = new DataTransfer();
    clipboardData.items.add(
      new File(["mock"], "pasted.png", { type: "image/png" }),
    );
    document.dispatchEvent(
      new ClipboardEvent("paste", { clipboardData, bubbles: true }),
    );
  });
  await expect(page.getByTestId("upload-receipt")).toContainText("pasted.png");
  await expect(page.getByTestId("upload-error")).toHaveText(
    dictionary.en["error.busy"],
  );
});
