import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

for (const lang of ["en", "bn"]) {
  test(`domain switch preserves the circuit workspace in ${lang}`, async ({
    page,
  }) => {
    await page.addInitScript(
      (lang) => localStorage.setItem("circuit-language", lang),
      lang,
    );
    await page.goto("/");
    await expect(page.locator("#readout tr")).toHaveCount(7);
    const selector = page.getByTestId("domain-switch");
    await expect(selector).toHaveValue("circuit");
    await expect(page.locator("#app")).toHaveAttribute(
      "data-domain",
      "circuit",
    );
    await page.locator('[data-tab="parameters"]').click();
    const value = page.locator('input[type="number"][data-param="R1"]');
    await value.fill("42");
    await selector.selectOption("mechanics");
    await expect(page.locator("#app")).toHaveAttribute(
      "data-domain",
      "mechanics",
    );
    await expect(page.getByTestId("mechanics-workspace")).toBeVisible();
    await expect(
      page.getByTestId("mechanics-workspace").locator("h1"),
    ).toHaveText(lang === "en" ? "Mechanics" : "বলবিদ্যা");
    await expect(page.getByTestId("mechanics-workspace")).toContainText(
      lang === "en" ? "Choose an image" : "শুরু করতে ছবি",
    );
    await expect(page.locator("#overlay")).toBeHidden();
    await page.locator("body").click({ position: { x: 1, y: 1 } });
    await page.keyboard.press("t");
    await page.keyboard.press("Escape");
    await expect(page.getByTestId("ocr-read-area")).not.toHaveClass(/active/);
    expect(
      (await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa"]).analyze())
        .violations,
    ).toEqual([]);
    await page.locator("#language").click();
    await expect(
      page.getByTestId("mechanics-workspace").locator("h1"),
    ).toHaveText(lang === "en" ? "বলবিদ্যা" : "Mechanics");
    await selector.selectOption("circuit");
    await expect(page.getByTestId("mechanics-workspace")).toHaveCount(0);
    await expect(page.locator("#overlay")).toBeVisible();
    await expect(value).toHaveValue("42");
    await expect(page.locator("#readout tr")).toHaveCount(7);
  });
}

test("circuit upload sends its domain, uses job stages, and cancels on unmount", async ({
  page,
}) => {
  const stages = ["received", "detect", "solve", "done"];
  await page.route("**/api/analyze/start", async (route) => {
    expect(route.request().postData()).toContain(
      'name="domain"\r\n\r\ncircuit',
    );
    await route.fulfill({
      json: {
        job_id: "domain-job",
        width: 1,
        height: 1,
        page_count: 1,
        domain: "circuit",
        stages,
      },
    });
  });
  let cancelled = false;
  await page.route("**/api/analyze/domain-job", async (route) => {
    if (route.request().method() === "DELETE") {
      cancelled = true;
      await route.fulfill({ json: { cancelled: true } });
    } else {
      await route.fulfill({
        json: {
          stage: "detect",
          stage_index: 1,
          stage_count: 4,
          percent: 33,
          elapsed_seconds: 0.1,
          partial: {},
          result: null,
          error: null,
        },
      });
    }
  });
  await page.goto("/");
  await expect(page.locator("#readout tr")).toHaveCount(7);
  await page.locator("#upload").setInputFiles({
    name: "diagram.png",
    mimeType: "image/png",
    buffer: Buffer.from(
      "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=",
      "base64",
    ),
  });
  await expect(page.getByTestId("analysis-stepper").locator("li")).toHaveCount(
    4,
  );
  await page.getByTestId("domain-switch").selectOption("mechanics");
  await expect.poll(() => cancelled).toBe(true);
  await expect(page.getByTestId("mechanics-workspace")).toBeVisible();
  await page.evaluate(() => {
    const transfer = new DataTransfer();
    transfer.items.add(
      new File(["ignored"], "inactive.png", { type: "image/png" }),
    );
    document.dispatchEvent(
      new ClipboardEvent("paste", { clipboardData: transfer }),
    );
  });
  await page.getByTestId("domain-switch").selectOption("circuit");
  await expect(page.getByTestId("upload-error")).toContainText("cancelled");
  await expect(page.locator("#readout tr")).toHaveCount(7);
});
