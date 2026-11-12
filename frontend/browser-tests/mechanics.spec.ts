import { test, expect, type Page } from "@playwright/test";
import { createServer, type ViteDevServer } from "vite";
import { fileURLToPath } from "node:url";
import { mkdir, writeFile } from "node:fs/promises";
import AxeBuilder from "@axe-core/playwright";

let server: ViteDevServer;
const base = "http://127.0.0.1:5175/mechanics-dev.html";
const names = [
  "projectile_ground",
  "projectile_cliff",
  "incline",
  "pendulum",
  "spring_horizontal",
  "spring_vertical",
  "atwood",
  "table_pulley",
  "incline_pulley",
  "collision",
];
const reports: Record<string, unknown> = {};
const output = fileURLToPath(
  new URL("../../.cache/m2-browser/", import.meta.url),
);
test.beforeAll(async () => {
  server = await createServer({
    configFile: fileURLToPath(
      new URL("../mechanics-dev.config.mjs", import.meta.url),
    ),
    configLoader: "native",
    root: fileURLToPath(new URL("../", import.meta.url)),
    server: {
      host: "127.0.0.1",
      port: 5175,
      strictPort: true,
      fs: { allow: [fileURLToPath(new URL("../../", import.meta.url))] },
    },
    logLevel: "warn",
  });
  await server.listen();
  await mkdir(output, { recursive: true });
});
test.afterAll(async () => {
  await writeFile(
    `${output}/measurements.json`,
    JSON.stringify(reports, null, 2),
  );
  await server?.close();
});
async function snapshot(page: Page) {
  return page.evaluate(() => structuredClone((window as any).mechanicsDev));
}
async function canvasPixels(page: Page) {
  return page.locator("#diagram").evaluate(async (el) => {
    const canvas = el as HTMLCanvasElement,
      data = canvas
        .getContext("2d")!
        .getImageData(0, 0, canvas.width, canvas.height).data;
    const digest = await crypto.subtle.digest("SHA-256", data);
    return {
      hash: Array.from(new Uint8Array(digest))
        .map((n) => n.toString(16).padStart(2, "0"))
        .join(""),
      png: canvas.toDataURL().split(",")[1],
    };
  });
}
async function open(page: Page, name: string, query = "") {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto(`${base}?fixture=${name}${query}`);
  await page.waitForFunction(() => (window as any).mechanicsDev?.ready);
  expect(errors).toEqual([]);
}

for (const name of names)
  test(`mechanics ${name}: composition and transport`, async ({ page }) => {
    const apiRequests: string[] = [];
    page.on("request", (request) => {
      if (new URL(request.url()).pathname.startsWith("/api"))
        apiRequests.push(request.url());
    });
    await open(page, name);
    const initial = await snapshot(page);
    expect(initial.frame0.passed, JSON.stringify(initial.frame0)).toBe(true);
    expect(initial.frame0.mean_absolute_channel).toBeLessThanOrEqual(2);
    expect(initial.frame0.fraction_over_16).toBeLessThanOrEqual(0.005);
    expect(initial.frame0.max_anchor_error_px).toBeLessThanOrEqual(1);
    expect(initial.playing).toBe(false);
    expect(initial.dpr).toBeLessThanOrEqual(2);
    await page.getByRole("button", { name: "Play", exact: true }).click();
    await page.waitForFunction(() => (window as any).mechanicsDev.time > 0.18);
    await page.getByRole("button", { name: "Pause", exact: true }).click();
    const paused = await snapshot(page);
    expect(paused.time).toBeGreaterThan(0);
    expect(paused.state.positions).not.toEqual(initial.state.positions);
    for (const body of initial.document.bodies.filter(
      (b: any) => b.on_surface,
    )) {
      const surface = initial.document.surfaces.find(
          (s: any) => s.id === body.on_surface,
        ),
        a = surface.polyline[0],
        b = surface.polyline.at(-1);
      const length = Math.hypot(b[0] - a[0], b[1] - a[1]),
        normal = [-(b[1] - a[1]) / length, (b[0] - a[0]) / length];
      const distance = (point: number[]) =>
        (point[0] - a[0]) * normal[0] + (point[1] - a[1]) * normal[1];
      const before = initial.draw.bodies.find(
          (b: any) => b.id === body.id,
        ).anchor,
        after = paused.draw.bodies.find((b: any) => b.id === body.id).anchor;
      expect(Math.abs(distance(after) - distance(before))).toBeLessThan(1);
    }
    await page.waitForTimeout(100);
    expect((await snapshot(page)).time).toBe(paused.time);
    await page.getByRole("button", { name: "Reset", exact: true }).click();
    expect((await snapshot(page)).time).toBe(0);
    await page.getByRole("button", { name: "Step", exact: true }).click();
    expect((await snapshot(page)).time).toBeCloseTo(1 / 240, 10);
    await page.getByRole("slider", { name: "Time", exact: true }).focus();
    await page.keyboard.press("ArrowRight");
    expect((await snapshot(page)).time).toBeGreaterThan(1 / 240);
    await page
      .getByRole("combobox", { name: "Speed", exact: true })
      .selectOption("4");
    await page.getByRole("button", { name: "Reset", exact: true }).click();
    await page.screenshot({ path: `${output}/${name}.png`, fullPage: true });
    const final = await snapshot(page);
    reports[name] = {
      frame0: initial.frame0,
      render_ms: final.renderTimes,
      raf_interval_ms: paused.frameIntervals,
      padding: final.padding,
    };
    expect(apiRequests).toEqual([]);
  });

test("mechanics pulley ropes preserve length and terminal bodies do not cross floors", async ({
  page,
}) => {
  const length = (points: number[][]) =>
    points
      .slice(1)
      .reduce(
        (sum, p, i) =>
          sum + Math.hypot(p[0] - points[i][0], p[1] - points[i][1]),
        0,
      );
  for (const name of ["atwood", "table_pulley", "incline_pulley"]) {
    await open(page, name);
    const before = await snapshot(page),
      ropeLength = length(before.draw.links[0].points);
    const time = page.getByRole("slider", { name: "Time", exact: true });
    await time.focus();
    await time.press("End");
    const terminal = await snapshot(page);
    expect(terminal.time).toBeCloseTo(terminal.duration, 5);
    expect(length(terminal.draw.links[0].points)).toBeCloseTo(ropeLength, 6);
    for (const body of terminal.document.bodies) {
      const target = terminal.draw.bodies.find((b: any) => b.id === body.id),
        half = (body.bbox[3] - body.bbox[1]) / 2;
      const floors = terminal.document.surfaces.filter(
        (s: any) =>
          s.type === "floor" &&
          s.polyline[0][1] > body.anchor[1] &&
          target.anchor[0] >= Math.min(...s.polyline.map((p: any) => p[0])) &&
          target.anchor[0] <= Math.max(...s.polyline.map((p: any) => p[0])),
      );
      for (const floor of floors)
        expect(target.anchor[1] + half).toBeLessThanOrEqual(
          floor.polyline[0][1] + 1,
        );
    }
  }
});

test("mechanics binding classes preserve background and geometry reset restores source", async ({
  page,
}) => {
  await open(page, "incline");
  const initial = await snapshot(page);
  const initialPixels = await canvasPixels(page);
  const mass = page.getByRole("spinbutton", { name: "mass B1 number" });
  await mass.fill("6");
  await mass.press("Tab");
  expect((await snapshot(page)).backgroundHash).toBe(initial.backgroundHash);
  expect((await snapshot(page)).document.bodies[0].mass.status).toBe("user");
  const position = page.getByRole("spinbutton", { name: "position number" });
  await position.fill("2.2");
  await position.press("Tab");
  const moved = await snapshot(page);
  expect(moved.backgroundHash).toBe(initial.backgroundHash);
  expect(moved.draw.bodies[0].anchor).not.toEqual(
    initial.draw.bodies[0].anchor,
  );
  const theta = page.getByRole("spinbutton", { name: "theta number" });
  await expect(theta).toBeDisabled();
  await page.getByRole("button", { name: "Unlock theta", exact: true }).click();
  await theta.fill("40");
  await theta.press("Tab");
  const changed = await snapshot(page);
  expect(changed.modified).toBe(true);
  expect(changed.backgroundHash).not.toBe(initial.backgroundHash);
  await expect(page.getByText("Modified", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Play", exact: true }).click();
  await page.waitForFunction(() => (window as any).mechanicsDev.time > 0.1);
  await mass.fill("7");
  await mass.press("Tab");
  const restarted = await snapshot(page);
  expect(restarted.playing).toBe(true);
  expect(restarted.time).toBeLessThan(0.15);
  await page.getByRole("button", { name: "Pause", exact: true }).click();
  await page
    .getByRole("button", { name: "Back to original", exact: true })
    .click();
  const restored = await snapshot(page);
  expect(restored.modified).toBe(false);
  expect(restored.backgroundHash).toBe(initial.backgroundHash);
  expect(restored.document).toEqual(initial.document);
  const restoredPixels = await canvasPixels(page);
  await writeFile(
    `${output}/reset-before.png`,
    Buffer.from(initialPixels.png, "base64"),
  );
  await writeFile(
    `${output}/reset-after.png`,
    Buffer.from(restoredPixels.png, "base64"),
  );
  expect(restoredPixels.hash).toBe(initialPixels.hash);
  await expect(theta).toBeDisabled();
});

for (const [name, handle] of [
  ["incline", "block"],
  ["pendulum", "bob"],
  ["spring_horizontal", "spring_end"],
  ["projectile_ground", "launch"],
])
  test(`mechanics drag ${handle} updates the same binding`, async ({
    page,
  }) => {
    await open(page, name);
    const before = await snapshot(page),
      h = before.draw.handles.find((h: any) => h.id === handle),
      box = await page.locator("#diagram").boundingBox();
    if (!box) throw new Error("No canvas");
    const x = box.x + before.padding.left + h.point[0],
      y = box.y + before.padding.top + h.point[1];
    await page.mouse.move(x, y);
    await page.mouse.down();
    await page.mouse.move(x + 40, y - 25, { steps: 5 });
    await page.mouse.up();
    const after = await snapshot(page);
    expect(Object.keys(after.params).length).toBeGreaterThan(0);
    expect(after.time).toBe(0);
    expect(after.backgroundHash).toBe(before.backgroundHash);
    if (handle === "launch")
      expect(
        after.draw.handles.find((h: any) => h.id === handle).point,
      ).not.toEqual(h.point);
    else
      expect(after.draw.bodies[0].anchor).not.toEqual(
        before.draw.bodies[0].anchor,
      );
  });

test("mechanics reduced motion, padding, DPR, accessibility and explicit degradation", async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await open(page, "projectile_ground");
  await page.waitForTimeout(150);
  expect((await snapshot(page)).time).toBe(0);
  await expect(page.getByText(/Reduced motion: still preview/)).toBeVisible();
  const speed = page.getByRole("spinbutton", { name: "launch speed number" });
  await speed.fill("40");
  await speed.press("Tab");
  const extended = await snapshot(page);
  expect(extended.padding.right).toBeGreaterThan(1000);
  const width = await page
    .locator("#diagram")
    .evaluate((el) => parseFloat((el as HTMLElement).style.width));
  expect(width).toBeGreaterThan(1800);
  const axe = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa"])
    .analyze();
  expect(axe.violations).toEqual([]);
  reports.accessibility = { violations: axe.violations };
  await page.goto(`${base}?fixture=pendulum&checkFault=1`);
  await page.waitForFunction(() => (window as any).mechanicsDev?.ready);
  const degraded = await snapshot(page);
  expect(degraded.frame0.passed).toBe(false);
  // Sparse ink can pass the RGB averages despite a large calibration error.
  expect(degraded.frame0.mean_absolute_channel).toBeLessThanOrEqual(2);
  expect(degraded.frame0.fraction_over_16).toBeLessThanOrEqual(0.005);
  expect(degraded.frame0.max_anchor_error_px).toBeGreaterThan(1);
  expect(degraded.degraded).toBe(true);
  expect(degraded.confidence).toBeLessThan(1);
  await expect(page.getByRole("alert")).toContainText(
    "untouched original with overlays only",
  );
  reports.degradation = degraded.frame0;
  await page.screenshot({ path: `${output}/degraded.png`, fullPage: true });
});

test("mechanics unknown objects stay in the document with the untouched source visible", async ({
  page,
}) => {
  await open(page, "incline", "&unknownType=1");
  const state = await snapshot(page);
  expect(state.document.bodies[0].type).toBe("unknown_fixture_object");
  expect(state.duration).toBe(0);
  expect(state.frame0.mean_absolute_channel).toBe(null);
  await expect(page.getByRole("alert")).toContainText("unknown_type");
  await expect(page.locator("#diagram")).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Play", exact: true }),
  ).toBeDisabled();
});

test("mechanics range dragging retains its control through live recomputation", async ({
  page,
}) => {
  await open(page, "incline");
  const slider = page.getByRole("slider", {
    name: "position range",
    exact: true,
  });
  const box = await slider.boundingBox();
  if (!box) throw new Error("No parameter slider");
  await page.mouse.move(box.x + box.width * 0.3, box.y + box.height / 2);
  await page.mouse.down();
  await page.mouse.move(box.x + box.width * 0.5, box.y + box.height / 2, {
    steps: 4,
  });
  const middle = (await snapshot(page)).params["params.start_position"];
  await page.mouse.move(box.x + box.width * 0.8, box.y + box.height / 2, {
    steps: 4,
  });
  await page.mouse.up();
  expect(
    (await snapshot(page)).params["params.start_position"],
  ).toBeGreaterThan(middle + 0.2);
});

test("mechanics phone view keeps native size, caps DPR and allows explicit stepping", async ({
  browser,
}) => {
  const context = await browser.newContext({
    viewport: { width: 390, height: 844 },
    deviceScaleFactor: 3,
    reducedMotion: "reduce",
  });
  try {
    const page = await context.newPage();
    await open(page, "pendulum");
    const state = await snapshot(page);
    expect(state.dpr).toBe(2);
    expect(state.time).toBe(0);
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
    expect(
      await page
        .locator("#diagram")
        .evaluate((el) => parseFloat((el as HTMLElement).style.width)),
    ).toBeGreaterThan(800);
    const viewport = page.locator(".canvas-scroll");
    await viewport.scrollIntoViewIfNeeded();
    const box = await viewport.boundingBox();
    if (!box) throw new Error("No phone viewport");
    const initialLeft = await viewport.evaluate((el) => el.scrollLeft);
    expect(initialLeft).toBeGreaterThan(0);
    const canvasBox = await page.locator("#diagram").boundingBox();
    if (!canvasBox) throw new Error("No phone canvas");
    const bobX =
      canvasBox.x + state.padding.left + state.draw.bodies[0].anchor[0];
    expect(bobX).toBeGreaterThan(box.x);
    expect(bobX).toBeLessThan(box.x + box.width);
    await page.mouse.move(box.x + box.width / 2, box.y + 30);
    await page.mouse.down();
    await page.mouse.move(box.x + box.width / 2 - 40, box.y + 30, { steps: 4 });
    await page.mouse.up();
    expect(await viewport.evaluate((el) => el.scrollLeft)).toBeGreaterThan(
      initialLeft + 20,
    );
    await page.getByRole("button", { name: "Step", exact: true }).click();
    expect((await snapshot(page)).time).toBeCloseTo(1 / 240, 10);
    await page.screenshot({
      path: `${output}/phone-pendulum.png`,
      fullPage: true,
    });
    await viewport.scrollIntoViewIfNeeded();
    await page.screenshot({ path: `${output}/phone-viewport.png` });
  } finally {
    await context.close();
  }
});
