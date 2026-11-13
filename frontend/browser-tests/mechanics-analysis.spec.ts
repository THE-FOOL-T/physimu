import { test, expect, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { spawn, type ChildProcess } from "node:child_process";
import { mkdirSync, writeFileSync } from "node:fs";
import path from "node:path";
const root = path.resolve(process.cwd(), ".."),
  base = "http://127.0.0.1:8007";
let server: ChildProcess,
  logs = "";
test.use({ baseURL: base });
test.beforeAll(async () => {
  server = spawn(
    path.join(
      root,
      ".venv",
      process.platform === "win32" ? "Scripts/python.exe" : "bin/python",
    ),
    ["-m", "circuit_sim.backend.tests.mechanics.stub_server", "--port", "8007"],
    {
      cwd: root,
      windowsHide: true,
      env: { ...process.env, PYTHONUTF8: "1" },
      stdio: ["ignore", "pipe", "pipe"],
    },
  );
  server.stdout?.on("data", (chunk) => {
    logs += chunk.toString();
  });
  server.stderr?.on("data", (chunk) => {
    logs += chunk.toString();
  });
  await expect
    .poll(
      async () => {
        if (server.exitCode !== null) throw new Error(logs);
        try {
          return (await fetch(base + "/api/domains")).status;
        } catch {
          return 0;
        }
      },
      { timeout: 20000 },
    )
    .toBe(200);
});
test.afterAll(async () => {
  server?.kill();
  mkdirSync(path.join(root, ".cache/m5-final"), { recursive: true });
  writeFileSync(
    path.join(root, ".cache/m5-final/browser-oracle-server.log"),
    logs,
  );
});
const state = (page: Page) =>
  page.evaluate(() => (window as any).mechanicsWorkspace);
const action = (page: Page, name: string) =>
  page.locator(`.mechanics-workspace [data-action="${name}"]`);
async function open(page: Page) {
  await page.goto("/");
  await page.getByTestId("domain-switch").selectOption("mechanics");
}
async function upload(page: Page, name: string) {
  await page
    .getByTestId("mechanics-image")
    .setInputFiles(path.join(root, `fixtures/mechanics/${name}.png`));
}
test("real HTTP oracle upload reports partial progress, then edits and plays the measured result", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await open(page);
  await upload(page, "pendulum");
  await expect.poll(async () => (await state(page)).analyzing).toBe(true);
  await expect
    .poll(async () => (await state(page)).analysisBoxes.length)
    .toBeGreaterThan(0);
  await expect(page.getByTestId("mechanics-analysis-status")).toContainText(
    /Reading labels|Measuring geometry/,
  );
  await expect(page.getByTestId("mechanics-analysis-status")).toContainText(
    "1 kg",
  );
  await expect.poll(async () => (await state(page)).analyzing).toBe(false);
  let s = await state(page);
  expect(s.project.scene.archetype).toBe("pendulum");
  expect(s.project.scene.meta.provenance).toBe("partial");
  expect(s.editing).toBe(true);
  expect(s.project.scene.links[0].a.ref).toBe("pivot");
  await expect(page.getByTestId("mechanics-notice")).toContainText(
    "does not establish correctness",
  );
  const value = page.locator(
    '.mechanics-workspace [data-value-path="bodies.B1.mass"]',
  );
  await value.fill("2");
  await value.press("Tab");
  expect((await state(page)).project.scene.bodies[0].mass.source).toBe("user");
  await action(page, "run").click();
  await expect(action(page, "play")).toBeEnabled();
  await action(page, "play").click();
  await expect.poll(async () => (await state(page)).time).toBeGreaterThan(0.05);
  await action(page, "pause").click();
  expect((await state(page)).playing).toBe(false);
  await page.screenshot({
    path: path.join(root, ".cache/m5-final/mechanics-upload-pendulum.png"),
    fullPage: true,
  });
  expect(errors).toEqual([]);
});
test("cancel and domain switch discard pending jobs and preserve user authoring", async ({
  page,
}) => {
  await open(page);
  await upload(page, "atwood");
  await expect(action(page, "cancel_analysis")).toBeVisible();
  await action(page, "cancel_analysis").click();
  await expect.poll(async () => (await state(page)).analyzing).toBe(false);
  await expect(
    page.locator('.mechanics-workspace [data-field="archetype"]'),
  ).toHaveValue("unsupported");
  await upload(page, "incline");
  await expect(action(page, "cancel_analysis")).toBeVisible();
  await page.getByTestId("domain-switch").selectOption("circuit");
  await page.getByTestId("domain-switch").selectOption("mechanics");
  await expect.poll(async () => (await state(page)).analyzing).toBe(false);
  await page.getByTestId("mechanics-fixture").selectOption("collision");
  await expect
    .poll(async () => (await state(page)).project.scene.archetype)
    .toBe("collision_1d");
});
test("missing mechanics weights retain editable native image; correction saving requires consent", async ({
  page,
}) => {
  await open(page);
  const pending = page.waitForResponse(
    (r) =>
      r.url().endsWith("/api/analyze/start") && r.request().method() === "POST",
  );
  const blank = await page.evaluate(() => {
    const c = document.createElement("canvas");
    c.width = 120;
    c.height = 80;
    const x = c.getContext("2d")!;
    x.fillStyle = "white";
    x.fillRect(0, 0, 120, 80);
    return c.toDataURL().split(",")[1];
  });
  await page.getByTestId("mechanics-image").setInputFiles({
    name: "blank.png",
    mimeType: "image/png",
    buffer: Buffer.from(blank, "base64"),
  });
  await pending;
  await expect(page.getByTestId("mechanics-notice")).toContainText("weights");
  expect((await state(page)).editing).toBe(true);
  expect((await state(page)).project.scene.bodies).toEqual([]);
  const consent = page.getByTestId("mechanics-correction-consent");
  await expect(consent).not.toBeChecked();
  let saves = 0;
  page.on("request", (r) => {
    if (r.url().endsWith("/api/corrections")) saves++;
  });
  await action(page, "save_correction").click();
  expect(saves).toBe(0);
  await consent.check();
  const saved = page.waitForResponse((r) =>
    r.url().endsWith("/api/corrections"),
  );
  await action(page, "save_correction").click();
  expect((await saved).status()).toBe(200);
  await expect(consent).not.toBeChecked();
  expect(saves).toBe(1);
});

test("phone Bangla analysis and consent controls fit and remain accessible", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await open(page);
  await page.getByRole("button", { name: "Switch language" }).click();
  await upload(page, "pendulum");
  await expect
    .poll(async () => (await state(page)).project?.scene.archetype)
    .toBe("pendulum");
  expect((await state(page)).editing).toBe(true);
  expect(
    await page.evaluate(
      () =>
        document.documentElement.scrollWidth <=
        document.documentElement.clientWidth,
    ),
  ).toBe(true);
  expect(
    (await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa"]).analyze())
      .violations,
  ).toEqual([]);
  await page.screenshot({
    path: path.join(root, ".cache/m5-final/phone-bn-analysis.png"),
    fullPage: true,
  });
});
